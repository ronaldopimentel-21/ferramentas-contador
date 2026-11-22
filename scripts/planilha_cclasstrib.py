"""Planilha Excel de cClassTrib, gerada a cada montagem do site a partir da base oficial da Receita (22/11/2026).

Abas: Leia-me, Operações do dia a dia (seleção da Seldon, IBS e CBS), IBS e CBS (todos), Imposto Seletivo (todos).
O campo `is` do dado marca a classificação do Imposto Seletivo: não tem percentual de redução e NÃO vale para IBS/CBS.
Uso no build: planilha_cclasstrib.gerar(rtc, caminho.xlsx) devolve a lista de códigos da seleção que sumiram da base (aviso, não erro:
a Receita pode retirar um código e isso não pode travar a atualização mensal do site).
"""
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

OPERACOES = {  # seleção curada da Seldon (não é lista oficial): código -> operação. Só IBS/CBS, conferida contra a descrição oficial.
    '410001': 'Bonificação', '410002': 'Transferência entre estabelecimentos',
    '410003': 'Doação e amostra grátis', '410026': 'Doação e amostra grátis',
    '410004': 'Exportação', '410013': 'Exportação', '410027': 'Exportação',
    '550001': 'Exportação', '550021': 'Exportação',
}
ORDEM = ['Bonificação', 'Transferência entre estabelecimentos', 'Doação e amostra grátis', 'Exportação']
CABECALHO = PatternFill('solid', fgColor='00132C')


def _pct(x, chave):
    v = x['red'].get(chave)
    return None if v is None else v / 100


def _aba(wb, titulo, cab, linhas, larguras, colunas_pct=()):
    ws = wb.create_sheet(titulo)
    ws.append(cab)
    for c in ws[1]:
        c.font, c.fill = Font(bold=True, color='FFFFFF'), CABECALHO
        c.alignment = Alignment(vertical='center', wrap_text=True)
    for linha in linhas:
        ws.append(linha)
    for i, w in enumerate(larguras, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(vertical='top', wrap_text=True)
            if c.column_letter in colunas_pct:
                c.number_format = '0%'
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions


def gerar(rtc, saida):
    todos = rtc['todos']
    ibs = [x for x in todos if not x['is']]
    sel = [x for x in todos if x['is']]
    wb = Workbook()
    ler = wb.active
    ler.title = 'Leia-me'
    texto = [
        ('cClassTrib: planilha para o escritório de contabilidade', True),
        ('', False),
        (f'Fonte: base oficial da Calculadora de Tributos da Receita Federal (versão {rtc["versao"]} de {rtc["data_versao"]}), '
         f'extraída em {rtc["extraido_em"]}. Licença MIT.', False),
        (f'Esta planilha tem {len(ibs)} códigos de IBS e CBS e {len(sel)} do Imposto Seletivo. São tabelas diferentes: '
         'a aba "Imposto Seletivo" não tem percentual de redução e não vale para o IBS/CBS.', False),
        ('A planilha aponta; quem classifica é você. Escolha pelo código e confirme a hipótese de uso com o contador responsável.', False),
        ('Atualizada todo mês, com a tabela completa e a consulta por NCM, em ferramentas.seldonsystems.com.br (grátis, sem cadastro).', False),
        ('', False),
        ('Abas: "Operações do dia a dia" (seleção da Seldon, não oficial: bonificação, transferência, doação e exportação), '
         '"IBS e CBS" (todos) e "Imposto Seletivo" (todos).', False),
        ('Seldon Systems · ferramentas.seldonsystems.com.br', False),
    ]
    for t, negrito in texto:
        ler.append([t])
        if negrito:
            ler.cell(ler.max_row, 1).font = Font(bold=True, size=14)
    ler.column_dimensions['A'].width = 110
    for row in ler.iter_rows():
        row[0].alignment = Alignment(wrap_text=True, vertical='top')

    ops = sorted(((OPERACOES[x['c']], x) for x in ibs if x['c'] in OPERACOES), key=lambda t: (ORDEM.index(t[0]), t[1]['c']))
    faltou = sorted(set(OPERACOES) - {x['c'] for _, x in ops})
    cab = ['Operação', 'cClassTrib', 'CST', 'Situação tributária', 'Descrição', 'Redução CBS', 'Redução IBS']
    _aba(wb, 'Operações do dia a dia', cab,
         [[g, x['c'], x['cst'], x['cstd'], x['d'], _pct(x, 'cbs'), _pct(x, 'ibs')] for g, x in ops], [26, 12, 7, 26, 80, 12, 12], ('F', 'G'))
    _aba(wb, 'IBS e CBS', cab[1:],
         [[x['c'], x['cst'], x['cstd'], x['d'], _pct(x, 'cbs'), _pct(x, 'ibs')] for x in ibs], [12, 7, 26, 80, 12, 12], ('E', 'F'))
    _aba(wb, 'Imposto Seletivo', ['cClassTrib (IS)', 'CST (IS)', 'Situação', 'Descrição'],
         [[x['c'], x['cst'], x['cstd'], x['d']] for x in sel], [14, 9, 26, 90])
    wb.save(saida)
    return faltou
