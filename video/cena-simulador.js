// Diretor de cena: cursor, legenda e cartão final por cima da ferramenta REAL (nada da ferramenta é simulado).
window.DIR = (() => {
  const css = `
  #dir-cursor{position:fixed;left:0;top:0;width:34px;height:34px;z-index:2147483646;pointer-events:none;transform:translate(-200px,-200px);transition:none;filter:drop-shadow(0 2px 3px rgba(0,0,0,.35))}
  #dir-ripple{position:fixed;width:46px;height:46px;border-radius:50%;border:3px solid #00B4D8;z-index:2147483645;pointer-events:none;opacity:0;transform:translate(-50%,-50%) scale(.3)}
  #dir-leg{position:fixed;left:18px;right:18px;top:18px;z-index:2147483644;pointer-events:none;background:#00132C;color:#fff;border-radius:14px;
    padding:16px 20px;font:800 27px/1.25 Montserrat,"Segoe UI",system-ui,sans-serif;box-shadow:0 8px 24px rgba(0,19,44,.35);
    opacity:0;transform:translateY(-12px);transition:opacity .35s,transform .35s;border-left:8px solid #00B4D8}
  #dir-leg.on{opacity:1;transform:none}
  #dir-chip{position:fixed;z-index:2147483645;pointer-events:none;background:#fff;border:2px solid #14213d;border-radius:8px;padding:8px 12px;
    font:600 16px "Segoe UI",sans-serif;color:#14213d;box-shadow:0 6px 16px rgba(0,0,0,.25);display:none;white-space:nowrap}
  #dir-fim{position:fixed;inset:0;z-index:2147483647;background:#00132C;color:#fff;display:flex;flex-direction:column;justify-content:center;
    align-items:center;text-align:center;padding:40px;opacity:0;transition:opacity .6s;pointer-events:none;font-family:Montserrat,"Segoe UI",sans-serif}
  #dir-fim.on{opacity:1}
  #dir-fim h2{font-size:44px;line-height:1.15;margin:0 0 22px;font-weight:800}
  #dir-fim p{font-size:24px;margin:8px 0;color:#d6e2ee}
  #dir-fim .url{margin-top:26px;font:700 26px Consolas,monospace;color:#00B4D8;border:2px dashed #00B4D8;padding:10px 16px;border-radius:8px}
  #dir-fim .siga{margin-top:30px;background:#00B4D8;color:#00132C;font-weight:800;font-size:26px;padding:14px 22px;border-radius:10px}
  #dir-ok{display:none}`;
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
  const cur = document.createElement('div'); cur.id = 'dir-cursor';
  cur.innerHTML = '<svg viewBox="0 0 24 24" width="34" height="34"><path d="M4 2l15 11.5-6.6.9 3.9 7.3-2.9 1.5-3.9-7.4L4 20z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>';
  const rip = document.createElement('div'); rip.id = 'dir-ripple';
  const leg = document.createElement('div'); leg.id = 'dir-leg';
  const chip = document.createElement('div'); chip.id = 'dir-chip';
  const fim = document.createElement('div'); fim.id = 'dir-fim';
  const ok = document.createElement('div'); ok.id = 'dir-ok';
  document.body.append(cur, rip, leg, chip, fim, ok);
  let x = innerWidth * 0.7, y = innerHeight * 0.8;
  const pos = () => { cur.style.transform = `translate(${x - 4}px,${y - 2}px)`; };
  pos();
  const espera = ms => new Promise(r => setTimeout(r, ms));
  const jit = (ms, f = 0.18) => ms * (1 - f + Math.random() * 2 * f);
  const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  function alvo(el) { const r = el.getBoundingClientRect(); return [r.left + r.width * (0.35 + Math.random() * 0.3), r.top + r.height * (0.4 + Math.random() * 0.2)]; }
  async function mover(tx, ty, ms) {
    ms = ms || jit(650 + Math.hypot(tx - x, ty - y) * 0.9);
    const x0 = x, y0 = y, cx = (x0 + tx) / 2 + (Math.random() - .5) * 120, cy = (y0 + ty) / 2 + (Math.random() - .5) * 80, t0 = performance.now();
    while (true) {
      const t = Math.min(1, (performance.now() - t0) / ms), e = ease(t);
      x = (1 - e) * (1 - e) * x0 + 2 * (1 - e) * e * cx + e * e * tx; y = (1 - e) * (1 - e) * y0 + 2 * (1 - e) * e * cy + e * e * ty;
      pos(); if (chip.style.display === 'block') { chip.style.left = (x + 18) + 'px'; chip.style.top = (y + 14) + 'px'; }
      if (t >= 1) break; await new Promise(requestAnimationFrame);
    }
  }
  async function ir(el, ms) { el.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); await espera(250); const [tx, ty] = alvo(el); await mover(tx, ty, ms); }
  async function clique(el) {
    await ir(el); await espera(jit(220));
    rip.style.left = x + 'px'; rip.style.top = y + 'px';
    rip.animate([{ opacity: .9, transform: 'translate(-50%,-50%) scale(.3)' }, { opacity: 0, transform: 'translate(-50%,-50%) scale(1.4)' }], { duration: 450 });
    await espera(120); el.click(); await espera(jit(350));
  }
  async function legenda(t, ms) { leg.classList.remove('on'); await espera(260); leg.innerHTML = t; leg.classList.add('on'); if (ms) await espera(ms); }
  async function digitar(el, texto) {
    await clique(el); el.focus();
    for (const ch of texto) { el.value += ch; el.dispatchEvent(new Event('input', { bubbles: true })); await espera(jit(ch === ' ' ? 210 : 140, .35)); }
  }
  async function rolar(dy, ms = 900) { const y0 = scrollY, t0 = performance.now();
    while (true) { const t = Math.min(1, (performance.now() - t0) / ms); scrollTo(0, y0 + dy * ease(t)); if (t >= 1) break; await new Promise(requestAnimationFrame); } }
  async function rolarEl(el, dy, ms = 900) { const y0 = el.scrollTop, t0 = performance.now();
    while (true) { const t = Math.min(1, (performance.now() - t0) / ms); el.scrollTop = y0 + dy * ease(t); if (t >= 1) break; await new Promise(requestAnimationFrame); } }
  async function arrastar(nomes, destino, soltar) {
    chip.innerHTML = nomes.map(n => '📄 ' + n).join('<br>');
    await mover(innerWidth * 0.82, innerHeight * 0.9, 500);
    chip.style.display = 'block'; chip.style.left = (x + 18) + 'px'; chip.style.top = (y + 14) + 'px';
    await espera(300); destino.scrollIntoView({ block: 'center', behavior: 'smooth' }); await espera(400);
    destino.classList.add('over'); const [tx, ty] = alvo(destino); await mover(tx, ty, 1500); await espera(350);
    chip.style.display = 'none'; destino.classList.remove('over'); await soltar(); await espera(200);
  }
  async function final(h, linhas, url) {
    leg.classList.remove('on');
    fim.innerHTML = `<h2>${h}</h2>${linhas.map(l => `<p>${l}</p>`).join('')}<div class="url">${url}</div><div class="siga">Siga @seldonsystems</div>`;
    fim.classList.add('on'); await espera(4200);
  }
  function pronto() { ok.textContent = 'FIM_VIDEO'; ok.style.display = 'block'; ok.style.position = 'fixed'; ok.style.left = '-9999px'; }
  return { espera, jit, mover, ir, clique, legenda, digitar, rolar, rolarEl, arrastar, final, pronto };
})();

// só na gravação: descrição oficial em até 3 linhas e letra maior, para caber no celular (dados iguais)
(() => {
  const st=document.createElement('style');
  st.textContent='.dir-clamp{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden} table td,table th{font-size:14.5px!important} .rf{font-size:13.5px!important}';
  document.head.appendChild(st);
  const envolver=()=>document.querySelectorAll('td.oficial:not([data-dir])').forEach(td=>{td.dataset.dir=1;td.innerHTML='<div class="dir-clamp">'+td.innerHTML+'</div>';});
  const alvo=document.getElementById('corpo'); if(alvo) new MutationObserver(envolver).observe(alvo,{childList:true});
})();

(async () => {
  const D = DIR, q = s => document.querySelector(s);
  document.querySelector('details.guia').open = false; scrollTo(0,0);
  await D.espera(600);
  await D.legenda('Quanto o produto do seu cliente vai pagar na Reforma?', 2600);
  await D.legenda('Solte os XMLs das notas.');
  await D.arrastar(['NFe-1001.xml','NFe-1002.xml'], q('#drop'), async () => {
    ITENS.push(...lerXML('exemplo-nfe-1001.xml', "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<nfeProc xmlns=\"http://www.portalfiscal.inf.br/nfe\" versao=\"4.00\"><NFe><infNFe Id=\"NFe-EXEMPLO-1001\" versao=\"4.00\">\n<ide><cUF>35</cUF><natOp>VENDA (EXEMPLO FICTICIO)</natOp><mod>55</mod><serie>1</serie><nNF>1001</nNF><dhEmi>2026-11-10T10:00:00-03:00</dhEmi><tpNF>1</tpNF><cMunFG>3550308</cMunFG></ide>\n<emit><CNPJ>00000000000000</CNPJ><xNome>EMPRESA EXEMPLO LTDA (FICTICIA)</xNome><enderEmit><UF>SP</UF></enderEmit></emit>\n<det nItem=\"1\"><prod><cProd>EX100101</cProd><xProd>ARROZ BRANCO TIPO 1 5KG</xProd><NCM>10063021</NCM><CFOP>5102</CFOP><uCom>UN</uCom><qCom>1</qCom><vProd>2500.00</vProd><vFrete>12.00</vFrete></prod>\n<imposto><ICMS><ICMS00><orig>0</orig><CST>00</CST><vBC>2512.00</vBC><pICMS>7.00</pICMS><vICMS>175.84</vICMS></ICMS00></ICMS>\n<PIS><PISAliq><CST>01</CST><vBC>2512.00</vBC><pPIS>1.65</pPIS><vPIS>41.45</vPIS></PISAliq></PIS>\n<COFINS><COFINSAliq><CST>01</CST><vBC>2512.00</vBC><pCOFINS>7.60</pCOFINS><vCOFINS>190.91</vCOFINS></COFINSAliq></COFINS></imposto></det>\n<det nItem=\"2\"><prod><cProd>EX100102</cProd><xProd>LEITE UHT INTEGRAL 1L</xProd><NCM>04012010</NCM><CFOP>5102</CFOP><uCom>UN</uCom><qCom>1</qCom><vProd>1800.00</vProd><vFrete>12.00</vFrete></prod>\n<imposto><ICMS><ICMS00><orig>0</orig><CST>00</CST><vBC>1812.00</vBC><pICMS>7.00</pICMS><vICMS>126.84</vICMS></ICMS00></ICMS>\n<PIS><PISAliq><CST>01</CST><vBC>1812.00</vBC><pPIS>1.65</pPIS><vPIS>29.90</vPIS></PISAliq></PIS>\n<COFINS><COFINSAliq><CST>01</CST><vBC>1812.00</vBC><pCOFINS>7.60</pCOFINS><vCOFINS>137.71</vCOFINS></COFINSAliq></COFINS></imposto></det>\n<det nItem=\"3\"><prod><cProd>EX100103</cProd><xProd>SABONETE BARRA 90G</xProd><NCM>34011190</NCM><CFOP>5102</CFOP><uCom>UN</uCom><qCom>1</qCom><vProd>600.00</vProd><vFrete>12.00</vFrete></prod>\n<imposto><ICMS><ICMS00><orig>0</orig><CST>00</CST><vBC>612.00</vBC><pICMS>18.00</pICMS><vICMS>110.16</vICMS></ICMS00></ICMS>\n<PIS><PISAliq><CST>01</CST><vBC>612.00</vBC><pPIS>1.65</pPIS><vPIS>10.10</vPIS></PISAliq></PIS>\n<COFINS><COFINSAliq><CST>01</CST><vBC>612.00</vBC><pCOFINS>7.60</pCOFINS><vCOFINS>46.51</vCOFINS></COFINSAliq></COFINS></imposto></det>\n<det nItem=\"4\"><prod><cProd>EX100104</cProd><xProd>CERVEJA LATA 350ML</xProd><NCM>22030000</NCM><CFOP>5102</CFOP><uCom>UN</uCom><qCom>1</qCom><vProd>1200.00</vProd><vFrete>12.00</vFrete></prod>\n<imposto><ICMS><ICMS00><orig>0</orig><CST>00</CST><vBC>1212.00</vBC><pICMS>25.00</pICMS><vICMS>303.00</vICMS></ICMS00></ICMS>\n<PIS><PISAliq><CST>01</CST><vBC>1212.00</vBC><pPIS>1.65</pPIS><vPIS>20.00</vPIS></PISAliq></PIS>\n<COFINS><COFINSAliq><CST>01</CST><vBC>1212.00</vBC><pCOFINS>7.60</pCOFINS><vCOFINS>92.11</vCOFINS></COFINSAliq></COFINS></imposto></det>\n<det nItem=\"5\"><prod><cProd>EX100105</cProd><xProd>PARAFUSO SEXTAVADO ZINCADO</xProd><NCM>73181500</NCM><CFOP>5102</CFOP><uCom>UN</uCom><qCom>1</qCom><vProd>350.00</vProd><vFrete>12.00</vFrete></prod>\n<imposto><ICMS><ICMS00><orig>0</orig><CST>00</CST><vBC>362.00</vBC><pICMS>18.00</pICMS><vICMS>65.16</vICMS></ICMS00></ICMS>\n<PIS><PISAliq><CST>01</CST><vBC>362.00</vBC><pPIS>1.65</pPIS><vPIS>5.97</vPIS></PISAliq></PIS>\n<COFINS><COFINSAliq><CST>01</CST><vBC>362.00</vBC><pCOFINS>7.60</pCOFINS><vCOFINS>27.51</vCOFINS></COFINSAliq></COFINS></imposto></det>\n</infNFe></NFe></nfeProc>")); ITENS.push(...lerXML('exemplo-nfe-1002.xml', "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<nfeProc xmlns=\"http://www.portalfiscal.inf.br/nfe\" versao=\"4.00\"><NFe><infNFe Id=\"NFe-EXEMPLO-1002\" versao=\"4.00\">\n<ide><cUF>35</cUF><natOp>VENDA (EXEMPLO FICTICIO)</natOp><mod>55</mod><serie>1</serie><nNF>1002</nNF><dhEmi>2026-11-10T10:00:00-03:00</dhEmi><tpNF>1</tpNF><cMunFG>3550308</cMunFG></ide>\n<emit><CNPJ>00000000000000</CNPJ><xNome>EMPRESA EXEMPLO LTDA (FICTICIA)</xNome><enderEmit><UF>SP</UF></enderEmit></emit>\n<det nItem=\"1\"><prod><cProd>EX100201</cProd><xProd>NOTEBOOK 15 POL 8GB</xProd><NCM>84713012</NCM><CFOP>5102</CFOP><uCom>UN</uCom><qCom>1</qCom><vProd>4200.00</vProd></prod>\n<imposto><ICMS><ICMS00><orig>0</orig><CST>00</CST><vBC>4200.00</vBC><pICMS>12.00</pICMS><vICMS>504.00</vICMS></ICMS00></ICMS>\n<PIS><PISAliq><CST>01</CST><vBC>4200.00</vBC><pPIS>1.65</pPIS><vPIS>69.30</vPIS></PISAliq></PIS>\n<COFINS><COFINSAliq><CST>01</CST><vBC>4200.00</vBC><pCOFINS>7.60</pCOFINS><vCOFINS>319.20</vCOFINS></COFINSAliq></COFINS></imposto></det>\n<det nItem=\"2\"><prod><cProd>EX100202</cProd><xProd>CAMISETA ALGODAO ADULTO</xProd><NCM>61091000</NCM><CFOP>5102</CFOP><uCom>UN</uCom><qCom>1</qCom><vProd>890.00</vProd></prod>\n<imposto><ICMS><ICMS00><orig>0</orig><CST>00</CST><vBC>890.00</vBC><pICMS>18.00</pICMS><vICMS>160.20</vICMS></ICMS00></ICMS>\n<PIS><PISAliq><CST>01</CST><vBC>890.00</vBC><pPIS>1.65</pPIS><vPIS>14.69</vPIS></PISAliq></PIS>\n<COFINS><COFINSAliq><CST>01</CST><vBC>890.00</vBC><pCOFINS>7.60</pCOFINS><vCOFINS>67.64</vCOFINS></COFINSAliq></COFINS></imposto></det>\n<det nItem=\"3\"><prod><cProd>EX100203</cProd><xProd>CIMENTO COMUM SACO 50KG</xProd><NCM>25232910</NCM><CFOP>5102</CFOP><uCom>UN</uCom><qCom>1</qCom><vProd>1450.00</vProd></prod>\n<imposto><ICMS><ICMS00><orig>0</orig><CST>00</CST><vBC>1450.00</vBC><pICMS>12.00</pICMS><vICMS>174.00</vICMS></ICMS00></ICMS>\n<PIS><PISAliq><CST>01</CST><vBC>1450.00</vBC><pPIS>1.65</pPIS><vPIS>23.93</vPIS></PISAliq></PIS>\n<COFINS><COFINSAliq><CST>01</CST><vBC>1450.00</vBC><pCOFINS>7.60</pCOFINS><vCOFINS>110.20</vCOFINS></COFINSAliq></COFINS></imposto></det>\n<det nItem=\"4\"><prod><cProd>EX100204</cProd><xProd>DIPIRONA 500MG CX 10 COMP</xProd><NCM>30049099</NCM><CFOP>5102</CFOP><uCom>UN</uCom><qCom>1</qCom><vProd>320.00</vProd></prod>\n<imposto><ICMS><ICMS00><orig>0</orig><CST>00</CST><vBC>320.00</vBC><pICMS>18.00</pICMS><vICMS>57.60</vICMS></ICMS00></ICMS>\n<PIS><PISAliq><CST>01</CST><vBC>320.00</vBC><pPIS>1.65</pPIS><vPIS>5.28</vPIS></PISAliq></PIS>\n<COFINS><COFINSAliq><CST>01</CST><vBC>320.00</vBC><pCOFINS>7.60</pCOFINS><vCOFINS>24.32</vCOFINS></COFINSAliq></COFINS></imposto></det>\n</infNFe></NFe></nfeProc>")); calc(); });
  await D.espera(400);
  await D.legenda('Carga de hoje x regime pleno, item a item.');
  await D.ir(q('#cards')); await D.espera(2600);
  await D.rolar(330, 1300); await D.espera(2600);
  await D.legenda('Troque o cenário: 2026, 2027 ou 2033.');
  await D.rolar(-260, 900);
  const cen = q('#cen');
  for (const v of ['2026','2027','2033']) { await D.clique(cen); cen.value = v; cen.dispatchEvent(new Event('change')); await D.espera(1700); }
  await D.legenda('NCM com mais de um enquadramento? Você confere e escolhe.');
  const sel = [...document.querySelectorAll('#corpo select')].find(s => s.closest('tr').querySelector('.flag:not(.is)'));
  if (sel) { await D.ir(sel); await D.espera(600); await D.clique(sel);
    sel.value = sel.options[0].value; sel.dispatchEvent(new Event('change')); }
  await D.espera(2600);
  await D.legenda('Exporta para Excel, pronto para o cliente.');
  await D.clique(q('#xls')); await D.espera(1500);
  await D.final('Simulador de impacto<br>da Reforma por produto', ['Grátis para contadores. Sem cadastro.', 'Regras conferidas com o motor oficial da Receita.', 'Atualizado todo mês.'], 'ferramentas.seldonsystems.com.br');
  D.pronto();
})();
