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
BASE = 'https://' + DOMINIO
INDEXNOW_KEY = 'b829fffa100f4133c9eafe86b61c9e61'  # a mesma dos sites do Tali e da raiz; é pública por desenho

# SEO (21/11/2026): o build injeta descrição, canonical, Open Graph e JSON-LD em cada página e gera robots.txt, sitemap.xml,
# llms.txt e a chave do IndexNow. Fonte única aqui; o robô mensal mantém. O cartão og-ferramentas.png sai de
# scripts/og-ferramentas.html (Chrome --headless --window-size=1200,630 --screenshot). Conferência no ar: curador de marketing
# do framework (automacoes/curador). Página sem estes itens = build para com erro.
ORG = {'@type': 'Organization', 'name': 'Seldon Gestão e Tecnologia', 'url': 'https://seldonsystems.com.br',
       'email': 'contato@seldonsystems.com.br'}
PAGINAS = {
    'index.html': {
        'url': BASE + '/',
        'desc': 'Analisador de NCM com cClassTrib e simulador de impacto da Reforma Tributária por produto. Grátis, sem cadastro, '
                'no navegador e com a base oficial da Receita.',
        'ld': {'@type': 'WebSite', 'name': 'Ferramentas grátis para contadores', 'inLanguage': 'pt-BR'},
    },
    'analisador-ncm.html': {
        'url': BASE + '/analisador-ncm.html',
        'desc': 'Confira a planilha de produtos do cliente: NCM vigente, 8 dígitos, cClassTrib e redução de IBS/CBS por NCM. '
                'Grátis, no navegador, sem enviar o arquivo.',
        'ld': {'@type': 'WebApplication', 'name': 'Analisador de NCM', 'applicationCategory': 'BusinessApplication',
               'operatingSystem': 'Navegador'},
    },
    'simulador-impacto.html': {
        'url': BASE + '/simulador-impacto.html',
        'desc': 'Leia os XMLs de NF-e e compare a carga de hoje (ICMS, PIS, Cofins, ISS) com 2026, 2027-2028 e o regime pleno '
                'da Reforma, item a item. Grátis.',
        'ld': {'@type': 'WebApplication', 'name': 'Simulador de impacto da Reforma por produto',
               'applicationCategory': 'BusinessApplication', 'operatingSystem': 'Navegador'},
    },
    'talao-de-notas.html': {
        'url': BASE + '/talao-de-notas.html',
        'desc': 'Programa grátis para Windows que emite NFS-e pelo Emissor Nacional com o certificado A1. A nota do mês vem '
                'preenchida e você confere o espelho antes.',
        'ld': {'@type': 'SoftwareApplication', 'name': 'Talão de notas', 'applicationCategory': 'BusinessApplication',
               'operatingSystem': 'Windows'},
    },
}


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
    aplicar_seo()
    for proibido in ('prefers-color-scheme', 'data-theme'):
        for f in os.listdir(SAIDA):
            if f.endswith('.html') and proibido in open(os.path.join(SAIDA, f), encoding='utf-8').read():
                falha(f'{f}: tema escuro automático ({proibido})')
    print('montado em _site:', feitos, '| NCM', qtd8, '| RTC', rtc['versao'])


def aplicar_seo():
    import html as H, re
    hoje = datetime.date.today().isoformat()
    for nome, p in PAGINAS.items():
        arq = os.path.join(SAIDA, nome)
        h = open(arq, encoding='utf-8').read()
        titulo = re.search(r'<title>([^<]*)</title>', h).group(1)
        if not 70 <= len(p['desc']) <= 165:
            falha(f'{nome}: descrição com {len(p["desc"])} caracteres (70 a 165)')
        ld = dict(p['ld'], **{'@context': 'https://schema.org', 'url': p['url'], 'description': p['desc'], 'publisher': ORG})
        if ld['@type'] != 'WebSite':
            ld.update({'isAccessibleForFree': True, 'inLanguage': 'pt-BR',
                       'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'BRL'}})
        d = H.escape(p['desc'], quote=True)
        bloco = '\n'.join([
            f'<meta name="description" content="{d}">',
            f'<link rel="canonical" href="{p["url"]}">',
            '<meta property="og:type" content="website">',
            '<meta property="og:locale" content="pt_BR">',
            '<meta property="og:site_name" content="Seldon · ferramentas para contadores">',
            f'<meta property="og:title" content="{H.escape(titulo, quote=True)}">',
            f'<meta property="og:description" content="{d}">',
            f'<meta property="og:url" content="{p["url"]}">',
            f'<meta property="og:image" content="{BASE}/img/og-ferramentas.png">',
            '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
            '<meta name="twitter:card" content="summary_large_image">',
            '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>',
        ])
        h = re.sub(r'<meta name="description"[^>]*>\n?', '', h, count=1)  # a descrição antiga da vitrine sai; vale a daqui
        h = h.replace('</title>', '</title>\n' + bloco, 1)
        for item in ('name="description"', 'rel="canonical"', 'og:title', 'application/ld+json'):
            if h.count(item) != 1:
                falha(f'{nome}: {item} aparece {h.count(item)} vezes (deve ser 1)')
        open(arq, 'w', encoding='utf-8').write(h)
    soltas = [f for f in os.listdir(SAIDA) if f.endswith('.html') and f not in PAGINAS]
    if soltas:
        falha(f'página sem SEO definido em PAGINAS: {soltas}')
    open(os.path.join(SAIDA, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(f'<url><loc>{p["url"]}</loc><lastmod>{hoje}</lastmod></url>' for p in PAGINAS.values())
        + '\n</urlset>\n')
    open(os.path.join(SAIDA, 'robots.txt'), 'w', encoding='utf-8').write(
        'User-agent: *\nAllow: /\n\n# Robôs de busca das IAs (para poder ser citado nas respostas)\n'
        + ''.join(f'User-agent: {b}\nAllow: /\n\n' for b in ('OAI-SearchBot', 'ChatGPT-User', 'PerplexityBot',
                                                            'Claude-SearchBot', 'Claude-User', 'Applebot'))
        + f'Sitemap: {BASE}/sitemap.xml\n')
    open(os.path.join(SAIDA, INDEXNOW_KEY + '.txt'), 'w', encoding='utf-8').write(INDEXNOW_KEY)
    open(os.path.join(SAIDA, 'llms.txt'), 'w', encoding='utf-8').write('\n'.join([
        '# Ferramentas grátis para contadores (Seldon)', '',
        '> Ferramentas gratuitas para o contador atravessar a Reforma Tributária (IBS, CBS, Imposto Seletivo). Rodam no navegador,',
        '> sem cadastro e sem servidor: os arquivos do cliente não saem do computador. Base oficial da Calculadora de Tributos da',
        '> Receita Federal e tabela NCM do Siscomex, atualizadas todo mês por robô.', '',
        '## Ferramentas', '',
        *[f'- [{p["ld"]["name"]}]({p["url"]}): {p["desc"]}' for k, p in PAGINAS.items() if k != 'index.html'], '',
        '## Limites', '',
        '- As ferramentas apontam e simulam; a classificação fiscal e a orientação ao cliente são do contador.',
        '- O simulador usa a carga destacada no documento, item a item; não considera créditos na cadeia nem regimes específicos.', '',
        '## Quem faz', '',
        '- Seldon Gestão e Tecnologia Ltda. · contato@seldonsystems.com.br · https://seldonsystems.com.br',
        f'- Atualizado em {br(hoje)}.', '']))


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--ncm' in a:
        baixar_ncm()
    if '--rtc' in a:
        extrair_rtc(a[a.index('--rtc') + 1])
    montar()
