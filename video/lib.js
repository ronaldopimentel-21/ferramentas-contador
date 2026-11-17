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
