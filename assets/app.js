/* Página de busca: segmentos, filtros, ordenação, simulador. Dados em assets/dados.js (gerado por scripts/build.py). */
(function () {
  'use strict';
  var D = window.DADOS;
  var C = D.corretor;
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
    { id: 'financiamento-direto', nome: 'Financiamento direto', filtro: temSeg('financiamento-direto') },
    { id: 'mcmv', nome: 'Minha Casa Minha Vida', filtro: temSeg('mcmv') },
    { id: 'investimento', nome: 'Investimento e renda', filtro: temSeg('investimento') },
    { id: 'alto-padrao', nome: 'Alto padrão', filtro: temSeg('alto-padrao') },
    { id: 'aluguel', nome: 'Aluguel', filtro: temSeg('aluguel') },
    { id: 'simulador', nome: 'Simulador', painel: true },
    { id: 'sobre', nome: 'Sobre o corretor', painel: true }
  ];

  var TIPOS = { apartamento: 'Apartamento', studio: 'Studio', casa: 'Casa', lote: 'Lote', sala: 'Sala comercial' };
  var STATUS = { lancamento: 'Lançamento', 'em-obra': 'Em obra', entregue: 'Pronto para morar' };

  var estado = { seg: 'todos', busca: '', cidade: '', bairro: '', tipo: '', precoMin: '', precoMax: '', quartos: 0, areaMin: '', status: '', construtora: '', ordem: 'relevancia' };

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
  function zap(texto) { return 'https://wa.me/' + C.whatsapp + '?text=' + encodeURIComponent(texto); }
  var $ = function (s) { return document.querySelector(s); };

  /* ---------- filtros ---------- */
  function passa(i) {
    var seg = SEGMENTOS.filter(function (s) { return s.id === estado.seg; })[0];
    if (seg && seg.filtro && !seg.filtro(i)) return false;
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
    var selos = '';
    if (STATUS[i.status]) selos += '<span class="selo">' + STATUS[i.status] + '</span>';
    if ((i.segmentos || []).indexOf('financiamento-direto') >= 0) selos += '<span class="selo ouro">Financiamento direto</span>';
    if ((i.segmentos || []).indexOf('alto-padrao') >= 0) selos += '<span class="selo ouro">Alto padrão</span>';
    var preco = i.preco != null
      ? '<div class="preco">' + brl(i.preco) + '<small>' + esc(i.precoNota || '') + '</small></div>'
      : '<div class="preco">Sob consulta<small>' + esc(i.precoNota || '') + '</small></div>';
    var specs = [];
    if (i.area) specs.push('<span>📐 ' + faixa(i.area, ' m²') + '</span>');
    if (i.quartos) specs.push('<span>🛏️ ' + faixa(i.quartos, i.quartos[1] === 1 ? ' quarto' : ' quartos', 'studio') + '</span>');
    if (i.entrega) specs.push('<span>🔑 ' + mesAno(i.entrega) + '</span>');
    return '<a class="card" href="imoveis/' + i.slug + '/">' +
      '<div class="foto"><img loading="lazy" src="' + esc(i.fotos[0] && i.fotos[0].src) + '" alt="' + esc(i.nome) + '">' +
      '<div class="selos">' + selos + '</div>' +
      (i.fotos.length > 1 ? '<span class="qtd-fotos">📷 ' + i.fotos.length + '</span>' : '') + '</div>' +
      '<div class="info">' + preco + '<h3>' + esc(i.nome) + '</h3>' +
      '<div class="local">' + esc(i.bairro) + ', ' + esc(i.cidade) + '/' + esc(i.uf) + '</div>' +
      '<div class="specs">' + specs.join('') + '</div>' +
      '<div class="rodape"><span>' + esc(i.construtora) + '</span><span>' + esc(TIPOS[i.tipo] || '') + '</span></div>' +
      '</div></a>';
  }

  function vazio() {
    var seg = SEGMENTOS.filter(function (s) { return s.id === estado.seg; })[0];
    return '<div class="vazio"><h3>Ainda não tem imóvel publicado aqui</h3>' +
      '<p>Tenho opções de ' + esc(seg ? seg.nome.toLowerCase() : 'imóveis') + ' que ainda não estão no site. Me chama que eu te mando as melhores.</p>' +
      '<a class="btn btn-zap" target="_blank" rel="noopener" href="' + zap('Olá Igor! Vi seu site e procuro opções em: ' + (seg ? seg.nome : '')) + '">' + ICONE_ZAP + ' Falar no WhatsApp</a></div>';
  }

  function contar() {
    SEGMENTOS.forEach(function (s) {
      var el = document.querySelector('[data-seg="' + s.id + '"] .n');
      if (el && s.filtro) el.textContent = LISTA.filter(s.filtro).length;
    });
  }

  function render() {
    var seg = SEGMENTOS.filter(function (s) { return s.id === estado.seg; })[0] || SEGMENTOS[0];
    document.querySelectorAll('.seg').forEach(function (b) { b.classList.toggle('ativo', b.dataset.seg === seg.id); });
    $('#area-lista').hidden = !!seg.painel;
    $('#painel-simulador').hidden = seg.id !== 'simulador';
    $('#painel-sobre').hidden = seg.id !== 'sobre';
    if (seg.painel) return;
    var l = ordenar(LISTA.filter(passa));
    $('#titulo-resultado').innerHTML = esc(seg.id === 'todos' ? 'Imóveis à venda' : seg.nome) + '<small>' + l.length + (l.length === 1 ? ' resultado' : ' resultados') + '</small>';
    $('#grade').innerHTML = l.length ? l.map(card).join('') : vazio();
    $('#ver-resultados').textContent = 'Ver ' + l.length + (l.length === 1 ? ' resultado' : ' resultados');
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
      if (SEGMENTOS.filter(function (s) { return s.id === estado.seg; })[0].painel) location.hash = 'todos';
      render();
      $('#area-lista').scrollIntoView({ behavior: 'smooth' });
    });
    $('#busca').addEventListener('input', function (e) { estado.busca = e.target.value.trim(); render(); });
    var abrir = function (sim) { $('.filtros').classList.toggle('aberto', sim); $('.veu').classList.toggle('aberto', sim); };
    $('#abrir-filtros').addEventListener('click', function () { abrir(true); });
    $('#fechar-filtros').addEventListener('click', function () { abrir(false); });
    $('#ver-resultados').addEventListener('click', function () { abrir(false); $('#area-lista').scrollIntoView({ behavior: 'smooth' }); });
    $('.veu').addEventListener('click', function () { abrir(false); });
  }

  function ligarSegmentos() {
    $('#segmentos').innerHTML = SEGMENTOS.map(function (s) {
      return '<a class="seg" href="#' + s.id + '" data-seg="' + s.id + '">' + esc(s.nome) + (s.filtro ? ' <span class="n"></span>' : '') + '</a>';
    }).join('');
    var ler = function () {
      var h = location.hash.replace('#', '');
      estado.seg = SEGMENTOS.some(function (s) { return s.id === h; }) ? h : 'todos';
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
    $('#s-zap').href = zap('Olá Igor! Fiz uma simulação no seu site: imóvel de ' + brl(v) + ', entrada de ' + brl(e) + ', parcela de ' + brl(parcela) + ' em ' + n + ' meses. Quais imóveis se encaixam?');
  }

  var ICONE_ZAP = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.2c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.3-.7-2.8-1.1-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.9s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.1 1 2.1 1.3 2.4 1.5.3.1.5.1.7-.1l.9-1.1c.2-.3.4-.2.7-.1l2 .9c.3.1.5.2.5.3.1.2.1.7-.1 1.3z"/></svg>';

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-zap]').forEach(function (a) {
      a.href = zap(a.dataset.zap || 'Olá Igor! Vi seu site de imóveis e quero mais informações.');
    });
    ligarFiltros();
    ligarSegmentos();
    contar();
    ['#s-valor', '#s-entrada', '#s-juros', '#s-prazo'].forEach(function (s) { $(s).addEventListener('input', simular); });
    simular();
  });
})();
