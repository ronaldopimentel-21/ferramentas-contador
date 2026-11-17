"""Monta o site das ferramentas em _site/.

uso:
  python scripts/build.py                       # monta com os dados que estão em dados/
  python scripts/build.py --ncm                 # antes, baixa a tabela NCM (BrasilAPI, espelho do Classif/Siscomex)
  python scripts/build.py --rtc <calculadora-pro.db>   # antes, extrai as regras da Calculadora RTC da Receita

Se um dado novo vier estranho (poucos códigos, arquivo vazio), o script para com erro e nada é publicado:
o site no ar continua com a última versão boa.
"""
import json, os, shutil, subprocess, sys, urllib.request, datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, 'dados')
SAIDA = os.path.join(RAIZ, '_site')
DOMINIO = 'ferramentas.seldonsystems.com.br'
URL_NCM = 'https://brasilapi.com.br/api/ncm/v1'


def falha(msg):
    print('ERRO:', msg)
    sys.exit(1)


def baixar_ncm():
    req = urllib.request.Request(URL_NCM, headers={'User-Agent': 'ferramentas-contador'})
    dados = json.loads(urllib.request.urlopen(req, timeout=180).read())
    oito = [x for x in dados if len(x.get('codigo', '').replace('.', '')) == 8]
    if len(oito) < 9000:
        falha(f'tabela NCM com só {len(oito)} códigos de 8 dígitos; esperado mais de 9.000')
    json.dump(dados, open(os.path.join(DADOS, 'tabela-ncm.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    meta = ler_meta(); meta['data_ncm'] = datetime.date.today().isoformat(); salvar_meta(meta)
    print('NCM:', len(dados), 'linhas,', len(oito), 'de 8 dígitos')


def extrair_rtc(db):
    saida = os.path.join(DADOS, 'reforma-ncm.json')
    subprocess.run([sys.executable, os.path.join(RAIZ, 'scripts', 'extrair_reforma.py'), db, saida], check=True)
    r = json.load(open(saida, encoding='utf-8'))
    if len(r['regras']) < 500 or len(r['cclasstrib']) < 10:
        falha(f"regras da Receita estranhas: {len(r['regras'])} regras, {len(r['cclasstrib'])} cClassTrib")


def ler_meta():
    p = os.path.join(DADOS, 'meta.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def salvar_meta(m):
    json.dump(m, open(os.path.join(DADOS, 'meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def br(d):
    return '/'.join(reversed(d[:10].split('-')))


def montar():
    ncm = json.load(open(os.path.join(DADOS, 'tabela-ncm.json'), encoding='utf-8'))
    rtc_txt = open(os.path.join(DADOS, 'reforma-ncm.json'), encoding='utf-8').read()
    rtc = json.loads(rtc_txt)
    meta = ler_meta()
    tab = json.dumps([[x['codigo'], x['descricao'], x['data_inicio'], x['data_fim']] for x in ncm],
                     ensure_ascii=False, separators=(',', ':'))
    qtd8 = sum(1 for x in ncm if len(x['codigo'].replace('.', '')) == 8)
    if os.path.exists(SAIDA):
        shutil.rmtree(SAIDA)
    shutil.copytree(os.path.join(RAIZ, 'vitrine'), SAIDA)
    shutil.copytree(os.path.join(RAIZ, 'exemplos'), os.path.join(SAIDA, 'exemplos'),
                    ignore=shutil.ignore_patterns('*.py'))
    feitos = {}
    for nome in ('analisador-ncm', 'simulador-impacto'):
        h = open(os.path.join(RAIZ, 'ferramentas', nome, 'modelo.html'), encoding='utf-8').read()
        h = h.replace('__TABELA__', tab).replace('__REFORMA__', rtc_txt).replace('__DATA_NCM__', br(meta.get('data_ncm', '')))
        if '__' + 'TABELA__' in h or '__' + 'REFORMA__' in h:
            falha(f'{nome}: marcador não substituído')
        open(os.path.join(SAIDA, nome + '.html'), 'w', encoding='utf-8').write(h)
        feitos[nome] = len(h) // 1024
    idx = os.path.join(SAIDA, 'index.html')
    h = open(idx, encoding='utf-8').read()
    h = (h.replace('__DATA__', br(datetime.date.today().isoformat()))
          .replace('__NCM_QTD__', f'{qtd8:,}'.replace(',', '.'))
          .replace('__RTC_VERSAO__', f"{rtc['versao']} ({br(rtc['data_versao'])})"))
    open(idx, 'w', encoding='utf-8').write(h)
    open(os.path.join(SAIDA, 'CNAME'), 'w').write(DOMINIO + '\n')
    open(os.path.join(SAIDA, '.nojekyll'), 'w').write('')
    json.dump({'montado_em': datetime.date.today().isoformat(), 'ncm_8_digitos': qtd8, 'data_ncm': meta.get('data_ncm'),
               'rtc_versao': rtc['versao'], 'rtc_data': rtc['data_versao'], 'kb': feitos},
              open(os.path.join(SAIDA, 'versao.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for proibido in ('prefers-color-scheme', 'data-theme'):
        for f in os.listdir(SAIDA):
            if f.endswith('.html') and proibido in open(os.path.join(SAIDA, f), encoding='utf-8').read():
                falha(f'{f}: tema escuro automático ({proibido})')
    print('montado em _site:', feitos, '| NCM', qtd8, '| RTC', rtc['versao'])


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--ncm' in a:
        baixar_ncm()
    if '--rtc' in a:
        extrair_rtc(a[a.index('--rtc') + 1])
    montar()
