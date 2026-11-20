// Conta cliques em botões marcados com data-conta. Guarda só dia + botão + página (Worker ir.seldonsystems.com.br).
// Sem cookie, sem IP, sem dado do usuário. Não conta quando o arquivo é aberto no computador.
(function () {
  if (!/(^|\.)seldonsystems\.com\.br$/.test(location.hostname) || !navigator.sendBeacon) return;
  var pag = location.pathname.replace(/\.html$/, '').replace(/^\/+|\/+$/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-') || 'index';
  var origem = ('ferramentas-' + pag).slice(0, 40).replace(/-+$/, '');
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('[data-conta]');
    if (a) navigator.sendBeacon('https://ir.seldonsystems.com.br/c/' + a.getAttribute('data-conta') + '?o=' + origem);
  });
})();
