// Conta cliques em botões marcados com data-conta. Guarda só dia + botão + página (Worker ir.seldonsystems.com.br)
// e, se a pessoa chegou por link próprio enviado pela Seldon (?c=apelido), esse apelido. Sem cookie, sem IP, sem dado do usuário.
// Não conta quando o arquivo é aberto no computador.
(function () {
  if (!/(^|\.)seldonsystems\.com\.br$/.test(location.hostname) || !navigator.sendBeacon) return;
  var pag = location.pathname.replace(/\.html$/, '').replace(/^\/+|\/+$/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-') || 'index';
  var origem = ('ferramentas-' + pag).slice(0, 40).replace(/-+$/, '');
  var cc = ''; try { var q = new URLSearchParams(location.search).get('c'); if (q && /^[a-z0-9-]{1,40}$/.test(q)) sessionStorage.setItem('seldon_c', q); cc = sessionStorage.getItem('seldon_c') || ''; } catch (e) {}
  if (cc) origem += '&c=' + cc;
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('[data-conta]');
    if (a) navigator.sendBeacon('https://ir.seldonsystems.com.br/c/' + a.getAttribute('data-conta') + '?o=' + origem);
  });
})();
