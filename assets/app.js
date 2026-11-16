/* Página inicial: objetivo (investir/morar), segmentos, filtros, ordenação, simulador.
   Dados em assets/dados.js (gerado por scripts/build.py). */
(function () {
  'use strict';
  var D = window.DADOS;
  var I = window.ICONES;
  var S = D.site;
  var LISTA = D.imoveis;

  var SEGMENTOS = [
    { id: 'todos', nome: 'Todos', filtro: function () { return true; } },
    { id: 'apartamentos', nome: 'Apartamentos', filtro: function (i) { return i.tipo === 'apartamento'; } },
    { id: 'studios', nome: 'Studios', filtro: function (i) { return i.tipo === 'studio'; } },
    { id: 'casas', nome: 'Casas', filtro: function (i) { return i.tipo === 'casa'; } },
    { id: 'lotes', nome: 'Lotes', filtro: function (i) { return i.tipo === 'lote'; } },
    { id: 'lancamentos', nome: 'Lançamentos', filtro: function (i) { return i.status === 'lancamento'; } },
    { id: 'proximo-entrega', nome: 'Próximo à entrega', filtro: function (i) { return i.status === 'em-obra' && mesesAte(i.entrega) <= 12; } },
    { id: 'prontos', nome: 'Prontos para morar', filtro: function (i) { return i.status === 'entregue'; } },
    { id: 'alto-padrao', nome: 'Alto padrão', filtro: temSeg('alto-padrao') },
    { id: 'financiamento-direto', nome: 'Financiamento direto', filtro: temSeg('financiamento-direto') },
    { id: 'airbnb', nome: 'Airbnb e curta temporada', filtro: temSeg('airbnb') },
    { id: 'mcmv', nome: 'Minha Casa Minha Vida', filtro: temSeg('mcmv') },
    { id: 'aluguel', nome: 'Aluguel', filtro: temSeg('aluguel') },
    { id: 'simulador', nome: 'Simulador', painel: true }
  ];
  var ATALHOS = { investir: 'investimento', morar: 'moradia' };

  var TIPOS = { apartamento: 'Apartamento', studio: 'Studio', casa: 'Casa', lote: 'Lote', sala: 'Sala comercial' };
  var STATUS = { lancamento: 'Lançamento', 'em-obra': 'Em obra', entregue: 'Pronto para morar' };

  var estado = { seg: 'todos', perfil: '', busca: '', cidade: '', bairro: '', tipo: '', precoMin: '', precoMax: '', quartos: 0, areaMin: '', status: '', construtora: '', ordem: 'relevancia' };

  function temSeg(s) { return function (i) { return (i.segmentos || []).indexOf(s) >= 0; }; }
  function mesesAte(ym) {
    if (!ym) return 999;
    var p = ym.split('-'), hoje = new Date();
    return (+p[0] - hoje.getFullYear()) * 12 + (+p[1] - 1 - hoje.getMonth());
  }
  function brl(v) { return 'R$ ' + Math.round(v).toLocaleString('pt-BR'); }
  function mesAno(ym) {
    if (!ym) return '';
    var m = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
    var p = ym.split('-');
    return m[+p[1] - 1] + '/' + p[0];
  }
  function faixa(a, sufixo, zero) {
    if (!a) return '';
    var f = function (n) { return n === 0 && zero ? zero : String(n).replace('.', ','); };
    return a[0] === a[1] ? f(a[0]) + sufixo : f(a[0]) + ' a ' + f(a[1]) + sufixo;
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function semAcento(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function zap(texto) { return 'https://wa.me/' + S.whatsapp + '?text=' + encodeURIComponent(texto); }
  function segAtual() { return SEGMENTOS.filter(function (s) { return s.id === estado.seg; })[0] || SEGMENTOS[0]; }
  function temPerfil(i) { return !estado.perfil || (i.perfil || []).indexOf(estado.perfil) >= 0; }
  var $ = function (s) { return document.querySelector(s); };

  /* ---------- filtros ---------- */
  function passa(i) {
    var seg = segAtual();
    if (seg.filtro && !seg.filtro(i)) return false;
    if (!temPerfil(i)) return false;
    if (estado.busca) {
      var alvo = semAcento([i.nome, i.bairro, i.cidade, i.construtora, i.resumo].join(' '));
      var ok = semAcento(estado.busca).split(/\s+/).every(function (t) { return alvo.indexOf(t) >= 0; });
      if (!ok) return false;
    }
    if (estado.cidade && i.cidade !== estado.cidade) return false;
    if (estado.bairro && i.bairro !== estado.bairro) return false;
    if (estado.tipo && i.tipo !== estado.tipo) return false;
    if (estado.construtora && i.construtora !== estado.construtora) return false;
    if (estado.status && i.status !== estado.status) return false;
    if (estado.quartos && (!i.quartos || i.quartos[1] < estado.quartos)) return false;
    if (estado.areaMin && (!i.area || i.area[1] < +estado.areaMin)) return false;
    if (estado.precoMin && i.preco != null && i.preco < +estado.precoMin) return false;
    if (estado.precoMax && i.preco != null && i.preco > +estado.precoMax) return false;
    return true;
  }

  function ordenar(l) {
    var o = estado.ordem;
    var n = function (v, alt) { return v == null || v === '' ? alt : v; };
    return l.slice().sort(function (a, b) {
      if (o === 'menor-preco') return n(a.preco, 1e12) - n(b.preco, 1e12);
      if (o === 'maior-preco') return n(b.preco, -1) - n(a.preco, -1);
      if (o === 'entrega') return mesesAte(a.entrega) - mesesAte(b.entrega);
      if (o === 'maior-area') return n(b.area && b.area[1], 0) - n(a.area && a.area[1], 0);
      return (b.destaque ? 1 : 0) - (a.destaque ? 1 : 0);
    });
  }

  /* ---------- render ---------- */
  function card(i) {
    var segs = i.segmentos || [];
    var selos = '';
    if (STATUS[i.status]) selos += '<span class="selo">' + STATUS[i.status] + '</span>';
    if (segs.indexOf('alto-padrao') >= 0) selos += '<span class="selo ouro">Alto padrão</span>';
    else if (segs.indexOf('financiamento-direto') >= 0) selos += '<span class="selo ouro">Financiamento direto</span>';
    var specs = [];
    if (i.area) specs.push('<span>' + I.area + faixa(i.area, ' m²') + '</span>');
    if (i.quartos) specs.push('<span>' + I.cama + faixa(i.quartos, i.quartos[1] === 1 ? ' quarto' : ' quartos', 'studio') + '</span>');
    if (i.entrega) specs.push('<span>' + I.chave + 'Entrega ' + mesAno(i.entrega) + '</span>');
    var preco = i.preco != null
      ? '<div><small>Valor de referência</small><b>' + brl(i.preco) + '</b></div>'
      : '<div><small>Valores</small><b>Sob consulta</b></div>';
    return '<a class="card" href="imoveis/' + i.slug + '/">' +
      '<div class="foto"><img loading="lazy" src="' + esc(i.fotos[0] && i.fotos[0].src) + '" alt="' + esc(i.nome) + '">' +
      '<div class="selos">' + selos + '</div>' +
      (i.fotos.length > 1 ? '<span class="qtd-fotos">' + I.foto + i.fotos.length + '</span>' : '') + '</div>' +
      '<div class="info"><span class="kick">' + esc(i.construtora) + ' · ' + esc(TIPOS[i.tipo] || '') + '</span>' +
      '<h3>' + esc(i.nome) + '</h3>' +
      '<div class="local">' + I.pin + esc(i.bairro) + ', ' + esc(i.cidade) + '/' + esc(i.uf) + '</div>' +
      '<div class="specs">' + specs.join('') + '</div>' +
      '<div class="preco">' + preco + '<span class="ver">Ver detalhes ›</span></div>' +
      '</div></a>';
  }

  function vazio() {
    var seg = segAtual();
    var oque = seg.id === 'todos' ? 'esse perfil' : seg.nome.toLowerCase();
    return '<div class="vazio"><h3>Em breve no site</h3>' +
      '<p>Temos opções de ' + esc(oque) + ' que ainda não foram publicadas. Fale com a Equipe Legacy e receba as melhores no seu WhatsApp.</p>' +
      '<a class="btn btn-zap" target="_blank" rel="noopener" href="' + zap('Olá! Vim pelo site da Legacy Empreendimentos e procuro opções em: ' + seg.nome) + '">' + I.zap + ' Falar no WhatsApp</a></div>';
  }

  function contar() {
    SEGMENTOS.forEach(function (s) {
      var el = document.querySelector('[data-seg="' + s.id + '"] .n');
      if (!el || !s.filtro) return;
      var n = LISTA.filter(function (i) { return s.filtro(i) && temPerfil(i); }).length;
      el.textContent = n ? n : '';
    });
  }

  function render() {
    var seg = segAtual();
    document.querySelectorAll('.seg').forEach(function (b) { b.classList.toggle('ativo', b.dataset.seg === seg.id); });
    document.querySelectorAll('[data-perfil]').forEach(function (b) { b.classList.toggle('ativo', b.dataset.perfil === estado.perfil); });
    $('#area-lista').hidden = !!seg.painel;
    $('#painel-simulador').hidden = seg.id !== 'simulador';
    contar();
    if (seg.painel) return;
    var l = ordenar(LISTA.filter(passa));
    var nome = seg.id === 'todos' ? (estado.perfil === 'investimento' ? 'Para investir' : estado.perfil === 'moradia' ? 'Para morar' : 'Empreendimentos') : seg.nome;
    $('#titulo-resultado').innerHTML = esc(nome) + '<small>' + l.length + (l.length === 1 ? ' resultado' : ' resultados') + '</small>';
    $('#grade').innerHTML = l.length ? l.map(card).join('') : vazio();
    $('#ver-resultados').textContent = 'Ver ' + l.length + (l.length === 1 ? ' resultado' : ' resultados');
  }

  function irParaLista() {
    var alvo = $('#explorar');
    var t = document.querySelector('.topo'), h = getComputedStyle(t).position === 'sticky' ? t.offsetHeight : 0;
    if (alvo) window.scrollTo({ top: alvo.getBoundingClientRect().top + window.pageYOffset - h + 20, behavior: 'smooth' });
  }

  /* ---------- opções dos selects ---------- */
  function preencher(sel, valores, rotulo) {
    var el = $(sel);
    var unicos = valores.filter(function (v, k, a) { return v && a.indexOf(v) === k; }).sort();
    el.innerHTML = '<option value="">' + rotulo + '</option>' + unicos.map(function (v) { return '<option>' + esc(v) + '</option>'; }).join('');
  }

  function ligarFiltros() {
    preencher('#f-cidade', LISTA.map(function (i) { return i.cidade; }), 'Todas as cidades');
    preencher('#f-bairro', LISTA.map(function (i) { return i.bairro; }), 'Todos os bairros');
    preencher('#f-construtora', LISTA.map(function (i) { return i.construtora; }), 'Todas');
    var campos = { '#f-cidade': 'cidade', '#f-bairro': 'bairro', '#f-tipo': 'tipo', '#f-construtora': 'construtora', '#f-status': 'status', '#f-preco-min': 'precoMin', '#f-preco-max': 'precoMax', '#f-area': 'areaMin', '#ordem': 'ordem' };
    Object.keys(campos).forEach(function (s) {
      $(s).addEventListener('input', function (e) { estado[campos[s]] = e.target.value; render(); });
    });
    document.querySelectorAll('[data-quartos]').forEach(function (b) {
      b.addEventListener('click', function () {
        var v = +b.dataset.quartos;
        estado.quartos = estado.quartos === v ? 0 : v;
        document.querySelectorAll('[data-quartos]').forEach(function (x) { x.classList.toggle('ativo', +x.dataset.quartos === estado.quartos); });
        render();
      });
    });
    $('#limpar').addEventListener('click', function () {
      ['cidade', 'bairro', 'tipo', 'construtora', 'status', 'precoMin', 'precoMax', 'areaMin', 'busca'].forEach(function (k) { estado[k] = ''; });
      estado.quartos = 0;
      document.querySelectorAll('.filtros select, .filtros input').forEach(function (el) { el.value = ''; });
      document.querySelectorAll('[data-quartos]').forEach(function (x) { x.classList.remove('ativo'); });
      $('#busca').value = '';
      render();
    });
    $('#form-busca').addEventListener('submit', function (e) {
      e.preventDefault();
      estado.busca = $('#busca').value.trim();
      if (segAtual().painel) location.hash = 'todos';
      render();
      irParaLista();
    });
    $('#busca').addEventListener('input', function (e) { estado.busca = e.target.value.trim(); render(); });
    var abrir = function (sim) { $('.filtros').classList.toggle('aberto', sim); $('.veu').classList.toggle('aberto', sim); };
    $('#abrir-filtros').addEventListener('click', function () { abrir(true); });
    $('#fechar-filtros').addEventListener('click', function () { abrir(false); });
    $('#ver-resultados').addEventListener('click', function () { abrir(false); irParaLista(); });
    $('.veu').addEventListener('click', function () { abrir(false); });
  }

  function ligarPerfil() {
    document.querySelectorAll('#perfil [data-perfil]').forEach(function (b) {
      b.addEventListener('click', function () { estado.perfil = b.dataset.perfil; render(); });
    });
    document.querySelectorAll('[data-ir-perfil]').forEach(function (b) {
      b.addEventListener('click', function () {
        estado.perfil = b.dataset.irPerfil;
        if (segAtual().painel) estado.seg = 'todos';
        render();
        irParaLista();
      });
    });
  }

  function ligarSegmentos() {
    $('#segmentos').innerHTML = SEGMENTOS.map(function (s) {
      return '<a class="seg" href="#' + s.id + '" data-seg="' + s.id + '">' + esc(s.nome) + (s.filtro ? ' <span class="n"></span>' : '') + '</a>';
    }).join('');
    document.querySelectorAll('.seg').forEach(function (a) {
      a.addEventListener('click', function (ev) {
        ev.preventDefault();
        history.replaceState(null, '', '#' + a.dataset.seg);
        estado.seg = a.dataset.seg;
        render();
        if ($('#explorar').getBoundingClientRect().top < 0) irParaLista();
      });
    });
    var ler = function () {
      var h = location.hash.replace('#', '');
      if (ATALHOS[h]) { estado.perfil = ATALHOS[h]; estado.seg = 'todos'; render(); irParaLista(); return; }
      if (SEGMENTOS.some(function (s) { return s.id === h; })) { estado.seg = h; render(); irParaLista(); return; }
      render();
    };
    window.addEventListener('hashchange', ler);
    ler();
  }

  /* ---------- simulador ---------- */
  function simular() {
    var v = +$('#s-valor').value || 0, e = +$('#s-entrada').value || 0;
    var juros = (+$('#s-juros').value || 0) / 100, n = +$('#s-prazo').value || 1;
    var fin = Math.max(v - e, 0);
    var parcela = juros > 0 ? fin * juros / (1 - Math.pow(1 + juros, -n)) : fin / n;
    $('#r-fin').textContent = brl(fin);
    $('#r-parcela').textContent = brl(parcela);
    $('#r-renda').textContent = brl(parcela / 0.3);
    $('#s-zap').href = zap('Olá! Fiz uma simulação no site da Legacy Empreendimentos: imóvel de ' + brl(v) + ', entrada de ' + brl(e) + ', parcela de ' + brl(parcela) + ' em ' + n + ' meses. Quais imóveis se encaixam?');
  }

  document.addEventListener('DOMContentLoaded', function () {
    var q = new URLSearchParams(location.search).get('q');
    if (q) { estado.busca = q; $('#busca').value = q; }
    ligarFiltros();
    ligarPerfil();
    ligarSegmentos();
    ['#s-valor', '#s-entrada', '#s-juros', '#s-prazo'].forEach(function (s) { $(s).addEventListener('input', simular); });
    simular();
  });
})();
