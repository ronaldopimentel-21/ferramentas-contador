"""Testes da tabela cClassTrib e da planilha (22/11/2026). Uso: python scripts/test_cclasstrib.py
Origem do teste: a página misturava os 29 cClassTrib do Imposto Seletivo com os 170 de IBS/CBS e mostrava "0% / 0%" nos do Imposto Seletivo.
Cada caso afirma o EFEITO no HTML ou no Excel gerado a partir de dados/reforma-ncm.json, não a forma do texto.
"""
import json, os, re, shutil, sys, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import paginas_ncm  # noqa: E402

ncm = json.load(open(os.path.join(RAIZ, 'dados', 'tabela-ncm.json'), encoding='utf-8'))
rtc = json.load(open(os.path.join(RAIZ, 'dados', 'reforma-ncm.json'), encoding='utf-8'))
ibs = [x for x in rtc['todos'] if not x['is']]
sel = [x for x in rtc['todos'] if x['is']]
falhas = []


def caso(nome, ok, detalhe=''):
    print(('ok    ' if ok else 'FALHA ') + nome + (f' ({detalhe})' if detalhe and not ok else ''))
    if not ok:
        falhas.append(nome)


tmp = tempfile.mkdtemp(prefix='cclasstrib-')
try:
    paginas_ncm.gerar(tmp, ncm, rtc, '01/01/2026', 'https://teste')
    html = open(os.path.join(tmp, 'tabela-cclasstrib.html'), encoding='utf-8').read()

    caso('base tem 170 de IBS/CBS e 29 do Imposto Seletivo (premissa do teste)', (len(ibs), len(sel)) == (170, 29), f'{len(ibs)}/{len(sel)}')

    # linha de tabela de 4 colunas com a coluna de redução: formato de IBS/CBS
    def linha_ibs(x):
        return f'<td class="cod">{x["c"]}</td><td>{x["cst"]}</td>'

    # nenhuma linha do Imposto Seletivo pode aparecer com "Redução CBS / IBS" (0% / 0%)
    ruins = [x['c'] for x in sel if re.search(rf'<td class="cod">{x["c"]}</td><td>{x["cst"]}</td><td>[^<]*{re.escape(x["d"][:20])}[^<]*</td><td>0% / 0%</td>', html)]
    caso('linha do Imposto Seletivo não aparece com "0% / 0%"', not ruins, f'{len(ruins)} linhas, ex.: {ruins[:3]}')

    caso('título separa IBS/CBS: "Todos os 170 cClassTrib de IBS e CBS"', 'Todos os 170 cClassTrib de IBS e CBS' in html)
    caso('não diz mais "Todos os 199 cClassTrib"', 'Todos os 199' not in html)
    caso('bloco próprio do Imposto Seletivo com a contagem 29', re.search(r'29 cClassTrib do Imposto Seletivo', html) is not None)
    caso('bloco do Imposto Seletivo avisa que é outra tabela', 'Não use estes códigos no IBS' in html)
    caso('link para baixar a planilha Excel', '/downloads/planilha-cclasstrib-ibs-cbs.xlsx' in html)

    # as operações do dia a dia só têm IBS/CBS: devolução 300001 é do Imposto Seletivo e não pode estar na tabela de operações
    ini = html.find('operações do dia a dia')
    fim = html.find('Todos os 170')
    bloco_ops = html[ini:fim] if ini >= 0 and fim > ini else ''
    caso('tabela de operações não traz o 300001 (devolução, Imposto Seletivo)', bool(bloco_ops) and '300001' not in bloco_ops)
    caso('tabela de operações traz o 410001 (bonificação, IBS/CBS)', '410001' in bloco_ops)

    # planilha
    import planilha_cclasstrib  # noqa: E402
    from openpyxl import load_workbook
    arq = os.path.join(tmp, 'p.xlsx')
    faltou = planilha_cclasstrib.gerar(rtc, arq)
    wb = load_workbook(arq)
    caso('planilha: aba IBS e CBS com 170 linhas', wb['IBS e CBS'].max_row - 1 == 170, str(wb['IBS e CBS'].max_row - 1))
    caso('planilha: aba Imposto Seletivo com 29 linhas', wb['Imposto Seletivo'].max_row - 1 == 29)
    caso('planilha: código mantém o zero à esquerda (texto)', wb['IBS e CBS']['A2'].value == '000001')
    caso('planilha: seleção curada toda encontrada na base', not faltou, str(faltou))
    wb.close()
finally:
    shutil.rmtree(tmp, ignore_errors=True)  # no Windows o Excel aberto pode impedir apagar; não é falha do teste

print()
if falhas:
    print(f'{len(falhas)} FALHA(S)')
    sys.exit(1)
print('tudo ok')
