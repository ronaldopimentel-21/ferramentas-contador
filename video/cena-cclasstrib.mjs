// Reel "Tabela cClassTrib atualizada" (22/11/2026): grava a página REAL no ritmo humano, legenda queimada, sem narração.
// Dados são a base oficial pública (não são fictícios); a legenda diz que a ferramenta aponta e quem classifica é o contador.
// Uso: node video/cena-cclasstrib.mjs <saida.mp4> [capa.jpg]
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { mkdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire("F:/Projetos/seldon-posto/package.json");
const { chromium } = require("@playwright/test");
const FF = "C:/ffmpeg/bin/ffmpeg.exe";
const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
const [saida, capa] = process.argv.slice(2);
const tmp = join(raiz, "video", "_cclasstrib");
mkdirSync(tmp, { recursive: true });

// [início s, legenda]
const LEG = [
  [0.4, "Tabela cClassTrib atualizada todo mês, grátis"],
  [4.2, "Bonificação, doação, transferência e exportação"],
  [11.5, "Cada código com o CST e a redução de CBS e IBS"],
  [19.0, "Os 170 códigos de IBS e CBS, separados por CST"],
  [28.0, "Quais NCM entram em cada cClassTrib"],
  [33.5, "Base oficial da Receita. A tabela aponta; quem classifica é você"],
];
const FIM = 38.5;

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 540, height: 960 }, locale: "pt-BR",
  recordVideo: { dir: tmp, size: { width: 540, height: 960 } },
});
const page = await ctx.newPage();
const tPagina = Date.now();
await page.goto("https://ferramentas.seldonsystems.com.br/tabela-cclasstrib.html", { waitUntil: "networkidle" });
const t0 = Date.now();
const ate = async (s) => { const falta = t0 + s * 1000 - Date.now(); if (falta > 0) await page.waitForTimeout(falta); };
// rola suave até o topo de um h2 (texto contido) menos uma folga
const rolarPara = (sel, folga, ms) => page.evaluate(([sel, folga, ms]) => new Promise((ok) => {
  const el = [...document.querySelectorAll("h2")].find((h) => h.textContent.includes(sel));
  const y0 = scrollY, y1 = el.getBoundingClientRect().top + scrollY - folga, t = performance.now();
  const e = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const f = () => { const k = Math.min(1, (performance.now() - t) / ms); scrollTo(0, y0 + (y1 - y0) * e(k)); k < 1 ? requestAnimationFrame(f) : ok(); }; f();
}), [sel, folga, ms]);
const rolar = (dy, ms) => page.evaluate(([dy, ms]) => new Promise((ok) => {
  const y0 = scrollY, t = performance.now(), e = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const f = () => { const k = Math.min(1, (performance.now() - t) / ms); scrollTo(0, y0 + dy * e(k)); k < 1 ? requestAnimationFrame(f) : ok(); }; f();
}), [dy, ms]);

await ate(4.2); await rolarPara("devolução, doação", 70, 1800);
await ate(8.5); await rolar(430, 2800);
await ate(11.5); await rolar(520, 3200);
await ate(19.0); await rolarPara("Todos os", 70, 2200);
await ate(22.5); await rolar(520, 3200);
await ate(25.8); await rolar(520, 2000);
await ate(28.0); await rolarPara("Quais NCM", 70, 2200);
await ate(31.5); await rolar(380, 2200);
await ate(FIM + 0.3);
const offset = (t0 - tPagina) / 1000;
await page.close(); const bruto = await page.video().path(); await ctx.close();

const p2 = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
const caixa = (txt) => `<!doctype html><style>:root{color-scheme:light}html,body{margin:0;width:1080px;height:1920px;background:transparent}
  div{position:absolute;left:48px;right:48px;bottom:120px;background:#00132C;color:#fff;border-left:12px solid #00B4D8;border-radius:22px;
  padding:30px 36px;font:800 50px/1.22 Montserrat,'Segoe UI',Arial,sans-serif;box-shadow:0 10px 30px rgba(0,19,44,.4)}</style><div>${esc(txt)}</div>`;
const cartao = `<!doctype html><style>:root{color-scheme:light}html,body{margin:0;width:1080px;height:1920px;background:#00132C;color:#fff;
  font-family:Montserrat,'Segoe UI',Arial,sans-serif;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}
  h1{font-size:84px;line-height:1.1;margin:0 70px 40px;font-weight:800}p{font-size:44px;margin:10px 60px;color:#d6e2ee}
  .u{margin-top:60px;font:700 46px Consolas,monospace;color:#00B4D8;border:4px dashed #00B4D8;padding:22px 30px;border-radius:16px}
  .s{margin-top:60px;background:#00B4D8;color:#00132C;font-weight:800;font-size:46px;padding:24px 40px;border-radius:18px}</style>
  <h1>Tabela cClassTrib<br>grátis para contador</h1><p>170 códigos de IBS e CBS, com CST e redução.</p><p>Atualizada todo mês.</p>
  <div class="u">ferramentas.seldonsystems.com.br</div><div class="s">Siga @seldonsystems</div>`;
const pngs = [];
for (let i = 0; i < LEG.length; i++) { await p2.setContent(caixa(LEG[i][1])); const f = join(tmp, `leg${i}.png`); await p2.screenshot({ path: f, omitBackground: true }); pngs.push(f); }
await p2.setContent(cartao); const fimPng = join(tmp, "fim.png"); await p2.screenshot({ path: fimPng });
await browser.close();

const dur = FIM + 3.5;
const ent = ["-ss", offset.toFixed(2), "-i", bruto];
const fil = ["[0:v]fps=30,scale=1080:1920:flags=lanczos,tpad=stop_mode=clone:stop_duration=10[v0]"];
let u = "v0";
LEG.forEach(([de], i) => {
  const a = i + 1 < LEG.length ? LEG[i + 1][0] : FIM;
  ent.push("-loop", "1", "-t", String(dur), "-i", pngs[i]);
  fil.push(`[${u}][${i + 1}:v]overlay=0:0:enable='between(t,${de},${a})'[v${i + 1}]`); u = `v${i + 1}`;
});
ent.push("-loop", "1", "-t", String(dur), "-i", fimPng);
fil.push(`[${u}][${LEG.length + 1}:v]overlay=0:0:enable='gte(t,${FIM})'[vf]`);
execFileSync(FF, ["-v", "error", "-y", ...ent, "-filter_complex", fil.join(";"), "-map", "[vf]", "-t", String(dur),
  "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", saida]);
if (capa) execFileSync(FF, ["-v", "error", "-y", "-ss", "13", "-i", saida, "-frames:v", "1", "-q:v", "2", capa]);
console.log(`ok: ${saida} (${dur.toFixed(1)} s, corte inicial ${offset.toFixed(2)} s)`);
if (!existsSync(saida)) process.exit(1);
