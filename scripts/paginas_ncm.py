"""Páginas abertas a partir dos dados oficiais (21/11/2026): tabela cClassTrib por NCM e capítulos da NCM com a coluna Reforma.

Por quê: as buscas com volume são "consulta ncm", "ncm + produto" (cerveja, parafuso, perfume...) e "tabela cclasstrib
atualizada" (Bing Keyword Research, Brasil, ago-nov/2026). A informação já está nos dados das ferramentas; aqui ela vira página
que o Google lê. PILOTO: só os capítulos de CAPITULOS_PILOTO; o resto só com OK do fundador depois de medir o piloto
(regra piloto-antes-de-operacao-em-massa). Fonte única dos textos e do visual destas páginas.
"""
import html, os, re

CAPITULOS_PILOTO = ['22', '33', '73']   # bebidas (cerveja, refrigerante), perfumaria, obras de ferro e aço (parafusos)
# Nome curto do capítulo para o título (o Google corta em ~60 caracteres). Capítulo sem nome aqui usa as 3 primeiras palavras.
CURTOS = {'22': 'bebidas', '33': 'perfumaria e cosméticos', '73': 'ferro e aço, parafusos'}

CSS = """
@font-face{font-family:M;src:url(/fontes/montserrat-medium.woff) format("woff");font-weight:500}
@font-face{font-family:M;src:url(/fontes/montserrat-extrabold.woff) format("woff");font-weight:800}
:root{color-scheme:light;--azul:#00132C;--ciano:#00B4D8;--link:#00607A;--papel:#f7f8fa;--verde:#166534}
*{box-sizing:border-box}
body{margin:0;background:var(--papel);color:#14202e;font:16px/1.55 "Segoe UI",system-ui,sans-serif}
a{color:var(--link)}
header{background:var(--azul);color:#fff}
.wrap{max-width:1040px;margin:0 auto;padding:0 22px}
.topo{display:flex;align-items:center;gap:12px;padding:16px 0}
.topo a{color:#fff;text-decoration:none;display:flex;align-items:center;gap:12px}
.topo img{width:36px;height:auto}
.marca{font-family:M;font-weight:800;letter-spacing:.5px;font-size:19px}
.marca span{font-weight:500;letter-spacing:4px;font-size:13px;margin-left:6px;color:#9fdcec}
.hero{padding:22px 0 30px}
.hero h1{font-family:M;font-weight:800;font-size:28px;line-height:1.2;margin:0 0 10px}
.hero p{color:#d6e2ee;margin:0;font-size:16.5px;max-width:820px}
.trilha{font-size:13.5px;color:#9fb5c9;margin:0 0 10px}.trilha a{color:#9fdcec}
main{padding:26px 0 10px}
.bloco{background:#fff;border:1px solid #dfe5ec;border-radius:10px;padding:18px 20px;margin:0 0 18px}
.bloco h2{font-family:M;font-weight:800;font-size:19px;margin:0 0 8px;color:var(--azul)}
table{width:100%;border-collapse:collapse;font-size:14.5px}
th{text-align:left;font-weight:700;color:#3d4b5a;border-bottom:2px solid #dfe5ec;padding:6px 8px}
td{border-bottom:1px solid #eef1f5;padding:6px 8px;vertical-align:top}
td.cod{font:600 14px Consolas,"Cascadia Mono",monospace;white-space:nowrap}
tr.pos td{background:#f1f5f9;font-weight:700}
.n1{padding-left:14px}.n2{padding-left:28px}.n3{padding-left:42px}
/* a assinatura: o selo da Reforma em cada linha */
.selo{display:inline-block;border:2px solid var(--verde);color:var(--verde);border-radius:5px;padding:1px 7px;font:700 12.5px/1.4 "Segoe UI",sans-serif;white-space:nowrap}
.selo.is{border-color:#b45309;color:#92400e}
.sem{color:#6b7785;font-size:13px}
.btn{display:inline-block;background:var(--ciano);color:var(--azul);font-weight:700;text-decoration:none;border-radius:6px;padding:10px 16px}
details{margin:6px 0}summary{cursor:pointer;color:var(--link)}
.limite{margin:4px 0 18px;font-size:14px;color:#3d4b5a;border-left:4px solid var(--ciano);padding:4px 0 4px 14px}
footer{font-size:13px;color:#56636f;padding:20px 0 34px}
@media (max-width:820px){.hero h1{font-size:23px}td,th{padding:5px 4px}}
"""

RODAPE = ('<footer><div class="wrap">Seldon Gestão e Tecnologia Ltda. · CNPJ 52.909.592/0001-62 · contato@seldonsystems.com.br · '
          '<a href="/">Ferramentas grátis para contador</a></div></footer>')


def _e(s):
    # a descrição oficial do Siscomex vem com marcação (<i>champagne</i>): tira a marcação, mostra só o texto
    return html.escape(re.sub(r'<[^>]+>', '', s or ''), quote=True)


def _pagina(titulo, trilha, h1, intro, corpo, data_br):
    return (f'<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{_e(titulo)}</title>\n'
            f'<link rel="icon" href="/img/favicon-64.png">\n<style>{CSS}</style></head><body>\n'
            f'<header><div class="wrap"><div class="topo"><a href="/"><img src="/img/logo.png" srcset="/img/logo@2x.png 2x" alt="">'
            f'<div class="marca">SELDON<span>FERRAMENTAS</span></div></a></div>\n'
            f'<div class="hero"><div class="trilha">{trilha}</div><h1>{_e(h1)}</h1><p>{intro}</p></div></div></header>\n'
            f'<main><div class="wrap">\n{corpo}\n'
            f'<p class="limite">Tabela de consulta montada com dados públicos e oficiais, atualizada em {data_br}. Ela aponta; a '
            f'classificação fiscal e a orientação ao cliente são do contador. A ausência de redução por NCM não significa que o '
            f'produto não tenha outro tratamento (regime específico, Simples Nacional, Zona Franca).</p>\n'
            f'</div></main>\n{RODAPE}\n</body></html>\n')


def _regra_do_codigo(cod8, regras):
    """Regra de maior prefixo que casa com o código (o RTC liga cClassTrib a prefixos de NCM)."""
    melhor = None
    for r in regras:
        if cod8.startswith(r['p']) and (melhor is None or len(r['p']) > len(melhor['p'])):
            melhor = r
    return melhor


def _selo(regra, cct):
    if not regra:
        return '<span class="sem">sem redução ligada ao NCM</span>'
    c = cct.get(regra['c'], {})
    red = c.get('red', {})
    cbs, ibs = red.get('cbs', 0), red.get('ibs', 0)
    txt = f"cClassTrib {regra['c']} · " + (f"redução {cbs:g}% CBS / {ibs:g}% IBS" if (cbs or ibs) else "sem redução")
    selo = f'<span class="selo" title="{_e(c.get("d", ""))} ({_e(regra.get("a", ""))})">{_e(txt)}</span>'
    if regra.get('is'):
        selo += ' <span class="selo is">Imposto Seletivo</span>'
    return selo


def gerar(saida, ncm, rtc, data_br, base):
    """Grava as páginas e devolve o dicionário de SEO de cada uma, no formato de PAGINAS do build.py."""
    regras, cct = rtc['regras'], rtc['cclasstrib']
    vigentes = [x for x in ncm if x.get('data_fim', '9999') >= '2026']
    paginas = {}
    os.makedirs(os.path.join(saida, 'ncm'), exist_ok=True)

    # --- capítulos piloto
    for cap in CAPITULOS_PILOTO:
        titulo_cap = next((x['descricao'] for x in vigentes if x['codigo'] == cap), '').rstrip('.')
        linhas, n8 = [], 0
        for x in vigentes:
            dig = x['codigo'].replace('.', '')
            if not dig.startswith(cap) or len(dig) == 2:
                continue
            desc = x['descricao']
            nivel = len(desc) - len(desc.lstrip('-'))
            desc = desc.lstrip('- ').strip()
            if len(dig) == 4:
                linhas.append(f'<tr class="pos"><td class="cod">{_e(x["codigo"])}</td><td colspan="2">{_e(desc)}</td></tr>')
            elif len(dig) == 8:
                n8 += 1
                linhas.append(f'<tr><td class="cod">{_e(x["codigo"])}</td><td class="n{min(nivel, 3)}">{_e(desc)}</td>'
                              f'<td>{_selo(_regra_do_codigo(dig, regras), cct)}</td></tr>')
            else:
                linhas.append(f'<tr><td class="cod">{_e(x["codigo"])}</td><td class="n{min(nivel, 3)}" colspan="2">{_e(desc)}</td></tr>')
        rel = f'ncm/capitulo-{cap}.html'
        h1 = f'NCM capítulo {cap}: {titulo_cap}'
        corpo = (f'<section class="bloco"><h2>Tabela NCM do capítulo {cap} com a Reforma Tributária</h2>'
                 f'<p>{n8} códigos de 8 dígitos vigentes. A coluna Reforma mostra o cClassTrib e a redução de CBS e IBS quando a base '
                 f'oficial da Receita liga o código a um anexo da Lei Complementar 214/2025.</p>'
                 f'<table><thead><tr><th>Código NCM</th><th>Descrição oficial</th><th>Reforma</th></tr></thead><tbody>'
                 + ''.join(linhas) + '</tbody></table></section>'
                 '<section class="bloco"><h2>Conferir a planilha inteira de uma vez</h2><p>O analisador de NCM confere a lista de '
                 'produtos do cliente (código vigente, 8 dígitos, descrição) e traz o cClassTrib de cada item. Grátis, no navegador.</p>'
                 '<a class="btn" href="/analisador-ncm.html">Abrir o analisador de NCM</a></section>')
        trilha = '<a href="/">Ferramentas</a> › <a href="/tabela-cclasstrib.html">Tabela cClassTrib</a> › Capítulo ' + cap
        intro = (f'Consulta NCM do capítulo {cap} ({_e(titulo_cap.lower())}): código, descrição oficial do Siscomex e, em cada '
                 f'linha, o cClassTrib e a redução de IBS e CBS da Reforma Tributária. Atualizada todo mês.')
        open(os.path.join(saida, rel), 'w', encoding='utf-8').write(
            _pagina(f'NCM capítulo {cap} ({CURTOS.get(cap) or " ".join(titulo_cap.split()[:3]).rstrip(",").lower()}): tabela com cClassTrib',
                    trilha, h1, intro, corpo, data_br))
        desc_seo = f'Consulta NCM do capítulo {cap} ({titulo_cap.lower()[:48]}): códigos, descrição oficial e cClassTrib com a redução de IBS e CBS.'
        if len(desc_seo) > 165:
            desc_seo = desc_seo[:162].rstrip() + '...'
        paginas[rel] = {'url': f'{base}/{rel}', 'desc': desc_seo,
                        'ld': {'@type': 'Dataset', 'name': h1, 'inLanguage': 'pt-BR',
                               'isBasedOn': 'https://portalunico.siscomex.gov.br/classif/'}}

    # --- tabela cClassTrib por NCM
    por_c = {}
    for r in regras:
        por_c.setdefault(r['c'], []).append(r)
    linhas, detalhes = [], []
    for c in sorted(cct):
        info, rs = cct[c], por_c.get(c, [])
        red = info.get('red', {})
        anexos = sorted({r.get('a', '').split(',')[0] for r in rs if r.get('a')})
        linhas.append(f'<tr><td class="cod">{_e(c)}</td><td>{_e(info.get("cst", ""))}</td><td>{_e(info.get("d", ""))}</td>'
                      f'<td>{red.get("cbs", 0):g}% / {red.get("ibs", 0):g}%</td><td>{len(rs)}</td></tr>')
        itens = []
        for r in sorted(rs, key=lambda r: r['p']):
            cap = r['p'][:2]
            alvo = f' (<a href="/ncm/capitulo-{cap}.html">capítulo {cap}</a>)' if cap in CAPITULOS_PILOTO else ''
            itens.append(f'<li><span class="cod">{_e(r["p"])}</span> · {_e(r.get("a", ""))}{" · Imposto Seletivo" if r.get("is") else ""}{alvo}</li>')
        detalhes.append(f'<details><summary>cClassTrib {_e(c)}: {len(rs)} prefixos de NCM ({_e(", ".join(anexos)[:80])})</summary>'
                        f'<ul>{"".join(itens)}</ul></details>')
    corpo = ('<section class="bloco"><h2>cClassTrib com redução ligada ao NCM</h2>'
             f'<p>Base oficial da Calculadora de Tributos da Receita Federal, versão {_e(rtc["versao"])} de {_e(rtc["data_versao"])}. '
             'Estão aqui os códigos de classificação tributária cuja redução depende do NCM do produto (anexos da LC 214/2025); '
             'os demais cClassTrib não dependem do NCM e não entram nesta tabela.</p>'
             '<table><thead><tr><th>cClassTrib</th><th>CST</th><th>Descrição</th><th>Redução CBS / IBS</th><th>Prefixos de NCM</th></tr></thead>'
             '<tbody>' + ''.join(linhas) + '</tbody></table></section>'
             '<section class="bloco"><h2>Quais NCM entram em cada cClassTrib</h2>' + ''.join(detalhes) + '</section>'
             '<section class="bloco"><h2>Tabela NCM com a coluna Reforma</h2><p>Capítulos já abertos: '
             + ', '.join(f'<a href="/ncm/capitulo-{c}.html">capítulo {c}</a>' for c in CAPITULOS_PILOTO)
             + '. Para a lista do cliente inteira, use o <a href="/analisador-ncm.html">analisador de NCM</a>.</p></section>')
    titulo = 'Tabela cClassTrib por NCM atualizada · Reforma Tributária'
    open(os.path.join(saida, 'tabela-cclasstrib.html'), 'w', encoding='utf-8').write(_pagina(
        titulo, '<a href="/">Ferramentas</a> › Tabela cClassTrib', 'Tabela cClassTrib por NCM, atualizada todo mês',
        'Código de classificação tributária (cClassTrib), CST e redução de IBS e CBS de cada NCM, direto da base oficial da '
        'Receita Federal. Grátis, sem cadastro.', corpo, data_br))
    paginas['tabela-cclasstrib.html'] = {
        'url': f'{base}/tabela-cclasstrib.html',
        'desc': 'Tabela cClassTrib atualizada com o CST e a redução de IBS e CBS de cada NCM, da base oficial da Receita. '
                'Grátis e atualizada todo mês.',
        'ld': {'@type': 'Dataset', 'name': 'Tabela cClassTrib por NCM', 'inLanguage': 'pt-BR',
               'isBasedOn': 'https://github.com/ReceitaFederal/calculadora-rtc-regime-regular'}}
    return paginas
