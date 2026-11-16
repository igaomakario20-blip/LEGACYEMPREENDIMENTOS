#!/usr/bin/env python3
"""Gera o site a partir de data/imoveis.json.

Saídas:
  assets/dados.js            dados e ícones usados pela página inicial
  index.html                 página inicial (apresentação, coleções, busca com filtros, simulador)
  imoveis/<slug>/index.html  uma página por empreendimento, com prévia para WhatsApp

Uso: python3 scripts/build.py
"""
import html
import json
import shutil
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITE_URL = "https://legacyempreendimentos.netlify.app/"

TIPOS = {"apartamento": "Apartamento", "studio": "Studio", "casa": "Casa", "lote": "Lote", "sala": "Sala comercial"}
STATUS = {"lancamento": "Lançamento", "em-obra": "Em obra", "entregue": "Pronto para morar"}
PERFIS = {"investimento": "Investimento", "moradia": "Moradia"}
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def svg(corpo, cheio=False):
    if cheio:
        return f'<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{corpo}</svg>'
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{corpo}</svg>'


ICONES = {
    "zap": svg('<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.2c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.3-.7-2.8-1.1-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.9s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.1 1 2.1 1.3 2.4 1.5.3.1.5.1.7-.1l.9-1.1c.2-.3.4-.2.7-.1l2 .9c.3.1.5.2.5.3.1.2.1.7-.1 1.3z"/>', True),
    "area": svg('<path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5"/>'),
    "cama": svg('<path d="M3 18v-7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v7M3 14h18M6 9V6h5v3M3 18v2M21 18v2"/>'),
    "chave": svg('<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3M14 9l2 2"/>'),
    "pin": svg('<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>'),
    "grafico": svg('<path d="M3 20h18M5 16l5-5 4 3 6-7M15 7h5v5"/>'),
    "casa": svg('<path d="M3 11l9-7 9 7M5 9.5V20h14V9.5M10 20v-6h4v6"/>'),
    "foto": svg('<rect x="3" y="6" width="18" height="14" rx="2"/><circle cx="12" cy="13" r="3.5"/><path d="M8 6l1.5-2h5L16 6"/>'),
}

e = lambda s: html.escape(str(s if s is not None else ""), quote=True)


def brl(v):
    return "R$ " + f"{round(v):,}".replace(",", ".")


def mes_ano(ym):
    if not ym:
        return ""
    a, m = ym.split("-")
    return f"{MESES[int(m) - 1]}/{a}"


def faixa(a, sufixo, zero=None):
    if not a:
        return ""
    f = lambda n: zero if (n == 0 and zero) else (f"{n:g}".replace(".", ","))
    return f"{f(a[0])}{sufixo}" if a[0] == a[1] else f"{f(a[0])} a {f(a[1])}{sufixo}"


def zap(numero, texto):
    return f"https://wa.me/{numero}?text={urllib.parse.quote(texto)}"


def cabeca(titulo, descricao, imagem, url, prefixo):
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<meta name="theme-color" content="#050607">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Legacy Empreendimentos">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:image" content="{e(imagem)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="{prefixo}img/marca/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefixo}assets/estilo.css">
</head>"""


def marca(prefixo):
    return f"""<a class="marca" href="{prefixo}" aria-label="Legacy Empreendimentos, início"><img src="{prefixo}img/marca/escudo.webp" alt="" width="46" height="52"><span><b>LEGACY</b><small>Empreendimentos</small></span></a>"""


def topo(s, prefixo):
    return f"""<header class="topo"><div class="container">
  {marca(prefixo)}
  <form class="busca" id="form-busca" action="{prefixo}" role="search">
    <input id="busca" name="q" type="search" placeholder="Bairro, empreendimento ou construtora" aria-label="Buscar">
    <button type="submit">Buscar</button>
  </form>
  <a class="btn-zap-topo" target="_blank" rel="noopener" href="{e(zap(s['whatsapp'], 'Olá! Vim pelo site da Legacy Empreendimentos e quero mais informações.'))}" aria-label="WhatsApp">{ICONES['zap']}<span>{e(s['whatsappTexto'])}</span></a>
</div></header>"""


def rodape(s, prefixo):
    return f"""<footer class="rodape-site"><div class="container">
  <div>{marca(prefixo)}<a class="zap" target="_blank" rel="noopener" href="{e(zap(s['whatsapp'], 'Olá! Vim pelo site da Legacy Empreendimentos.'))}">{ICONES['zap']} {e(s['whatsappTexto'])}</a></div>
  <p>{e(s['rodape'])}.<br>Preços e condições conforme a tabela de cada construtora, sujeitos a alteração sem aviso. Imagens ilustrativas fornecidas pelas construtoras.</p>
</div></footer>"""


def peca(i, prefixo=""):
    preco = brl(i["preco"]) if i.get("preco") is not None else "Valores sob consulta"
    foto = i["fotos"][0]["src"]
    return (f'<a class="peca" href="{prefixo}imoveis/{e(i["slug"])}/"><img loading="lazy" src="{prefixo}{e(foto)}" alt="{e(i["nome"])}">'
            f'<div class="txt"><small>{e(i["construtora"])} · {e(i["bairro"])}</small><b>{e(i["nome"])}</b><span>{e(preco)}</span></div></a>')


def peca_breve(s, b):
    msg = f"Olá! Vi o {b['nome']} ({b['construtora']}) no site da Legacy Empreendimentos e quero receber a apresentação."
    return (f'<a class="peca breve" target="_blank" rel="noopener" href="{e(zap(s["whatsapp"], msg))}"><img class="escudo-d" src="img/marca/escudo.webp" alt="" loading="lazy"><span class="marca-d">{e(b["construtora"])}</span>'
            f'<div class="txt"><small>Apresentação exclusiva</small><b>{e(b["nome"])}</b><span>{ICONES["zap"]} Pedir apresentação</span></div></a>')


def secao_colecoes(d):
    s = d["site"]
    por_slug = {i["slug"]: i for i in d["imoveis"]}
    breve = {b["slug"]: b for b in d.get("embreve", [])}
    blocos = []
    for n, c in enumerate(d.get("colecoes", []), 1):
        pecas = []
        for slug in c["itens"]:
            if slug in por_slug:
                pecas.append(peca(por_slug[slug]))
            elif slug in breve:
                pecas.append(peca_breve(s, breve[slug]))
        blocos.append(f"""<div class="colecao" id="colecao-{e(c['id'])}">
    <div class="colecao-topo"><div><span class="num">{n:02d}</span><h3>{e(c['titulo'])}</h3><p>{e(c['sub'])}</p></div><span class="etiqueta">{e(c['construtoras'])}</span></div>
    <div class="trilho">{''.join(pecas)}</div>
  </div>""")
    return f"""<section class="secao" id="colecoes"><div class="container">
  <span class="kicker">Coleções Legacy</span>
  <h2 class="titulo-sec">Uma curadoria para cada estratégia</h2>
  <p class="sub-sec">Empreendimentos escolhidos pelo objetivo de quem compra: patrimônio de alto padrão, entrada acessível em boa localização ou renda com locação de curta temporada.</p>
  {''.join(blocos)}
</div></section>"""


def pagina_index(d):
    s = d["site"]
    titulo = "Legacy Empreendimentos · imóveis para investir e morar em Goiânia"
    desc = "Lançamentos selecionados das melhores construtoras de Goiânia, com preço, metragem, localização e entrega. Filtre por investimento ou moradia e fale com a Equipe Legacy no WhatsApp."
    return f"""{cabeca(titulo, desc, SITE_URL + 'img/marca/hero.webp', SITE_URL, '')}
<body>
{topo(s, '')}
<section class="hero">
  <div class="fundo" style="background-image:url(img/marca/hero.webp)"></div>
  <div class="container">
    <span class="kicker">Investimento imobiliário · Goiânia</span>
    <h1>Imóveis selecionados para <em>investir</em> e para <em>viver</em></h1>
    <p class="lead">Lançamentos das construtoras mais sólidas de Goiânia, com preço, metragem, localização e prazo de entrega lado a lado. Atendimento direto com a Equipe Legacy.</p>
    <p class="objetivo-t">Qual é o seu objetivo?</p>
    <div class="escolhas">
      <button type="button" class="escolha" data-ir-perfil="investimento"><span class="ic">{ICONES['grafico']}</span><span><b>Investir</b><small>Rentabilidade, valorização na planta e renda com aluguel.</small></span><span class="seta">→</span></button>
      <button type="button" class="escolha" data-ir-perfil="moradia"><span class="ic">{ICONES['casa']}</span><span><b>Morar</b><small>Conforto, lazer completo e os melhores endereços para a sua família.</small></span><span class="seta">→</span></button>
    </div>
    <div class="numeros"><div><b>Tabelas</b>direto das construtoras</div><div><b>ROI</b>simulação de retorno</div><div><b>WhatsApp</b>atendimento da equipe</div></div>
  </div>
</section>

{secao_colecoes(d)}

<section id="explorar">
  <div class="container explorar-topo">
    <span class="kicker">Explore</span>
    <h2 class="titulo-sec">Todos os empreendimentos</h2>
    <div class="perfil-bar"><span class="rot">Seu objetivo</span>
      <div class="alternar" id="perfil" role="group" aria-label="Objetivo">
        <button type="button" data-perfil="" class="ativo">Todos</button>
        <button type="button" data-perfil="investimento">{ICONES['grafico']} Investir</button>
        <button type="button" data-perfil="moradia">{ICONES['casa']} Morar</button>
      </div>
    </div>
  </div>
  <nav class="segmentos" aria-label="Segmentos"><div class="container" id="segmentos"></div></nav>

  <main class="container">
    <div class="lista-layout" id="area-lista">
      <div class="veu"></div>
      <aside class="filtros" aria-label="Filtros">
        <h3>Filtros <span><button type="button" id="limpar">Limpar</button> <button type="button" id="fechar-filtros" class="so-celular">Fechar</button></span></h3>
        <div class="grupo"><label class="t" for="f-cidade">Cidade</label><select id="f-cidade"></select></div>
        <div class="grupo"><label class="t" for="f-bairro">Bairro</label><select id="f-bairro"></select></div>
        <div class="grupo"><label class="t" for="f-tipo">Tipo de imóvel</label>
          <select id="f-tipo"><option value="">Todos</option>{''.join(f'<option value="{k}">{v}</option>' for k, v in TIPOS.items())}</select></div>
        <div class="grupo"><label class="t">Preço (R$)</label><div class="duo">
          <input id="f-preco-min" type="number" inputmode="numeric" placeholder="Mínimo" min="0" step="10000">
          <input id="f-preco-max" type="number" inputmode="numeric" placeholder="Máximo" min="0" step="10000"></div></div>
        <div class="grupo"><label class="t">Quartos</label><div class="pills">
          <button type="button" class="pill" data-quartos="1">1+</button><button type="button" class="pill" data-quartos="2">2+</button>
          <button type="button" class="pill" data-quartos="3">3+</button><button type="button" class="pill" data-quartos="4">4+</button></div></div>
        <div class="grupo"><label class="t" for="f-area">Área mínima (m²)</label><input id="f-area" type="number" inputmode="numeric" placeholder="Ex.: 60" min="0"></div>
        <div class="grupo"><label class="t" for="f-status">Fase da obra</label>
          <select id="f-status"><option value="">Todas</option>{''.join(f'<option value="{k}">{v}</option>' for k, v in STATUS.items())}</select></div>
        <div class="grupo"><label class="t" for="f-construtora">Construtora</label><select id="f-construtora"></select></div>
        <button type="button" class="btn btn-cromo btn-ver" id="ver-resultados">Ver resultados</button>
      </aside>
      <section>
        <div class="resultado-topo">
          <h2 id="titulo-resultado">Empreendimentos</h2>
          <div class="ordenar">
            <button type="button" class="btn-filtros" id="abrir-filtros">Filtros</button>
            <label for="ordem">Ordenar</label>
            <select id="ordem"><option value="relevancia">Destaques</option><option value="menor-preco">Menor preço</option><option value="maior-preco">Maior preço</option><option value="entrega">Entrega mais próxima</option><option value="maior-area">Maior área</option></select>
          </div>
        </div>
        <div class="grade" id="grade"></div>
      </section>
    </div>

    <section id="painel-simulador" class="lista-layout" hidden><div></div><div class="painel">
      <h2>Simulador de financiamento</h2>
      <p class="sub">Uma conta rápida para ter ideia da parcela. Tabela Price, sem correção. O valor final depende do banco e da análise de crédito.</p>
      <div class="sim-grade">
        <label>Valor do imóvel (R$)<input id="s-valor" type="number" inputmode="numeric" value="450000" min="0" step="1000"></label>
        <label>Entrada (R$)<input id="s-entrada" type="number" inputmode="numeric" value="90000" min="0" step="1000"></label>
        <label>Juros ao mês (%)<input id="s-juros" type="number" inputmode="decimal" value="1" min="0" step="0.05"></label>
        <label>Prazo (meses)<input id="s-prazo" type="number" inputmode="numeric" value="360" min="1" max="420"></label>
      </div>
      <div class="sim-res">
        <div><small>Valor financiado</small><b id="r-fin">-</b></div>
        <div><small>Parcela estimada</small><b id="r-parcela">-</b></div>
        <div><small>Renda familiar sugerida</small><b id="r-renda">-</b></div>
      </div>
      <p class="nota">Renda sugerida considera parcela de até 30% da renda, regra comum dos bancos.</p>
      <p style="margin-top:20px;display:flex;gap:18px;flex-wrap:wrap;align-items:center"><a class="btn btn-zap" id="s-zap" target="_blank" rel="noopener" href="#">{ICONES['zap']} Quero opções nessa faixa</a>
      <a class="link-sutil" target="_blank" rel="noopener" href="{e(s['roiUrl'])}">{ICONES['grafico']} Investidor? Calcule o retorno (ROI)</a></p>
    </div></section>
  </main>
</section>
{rodape(s, '')}
<a class="zap-flutuante" target="_blank" rel="noopener" aria-label="Falar no WhatsApp" href="{e(zap(s['whatsapp'], 'Olá! Vim pelo site da Legacy Empreendimentos e quero mais informações.'))}">{ICONES['zap']}</a>
<script src="assets/dados.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
"""


def pagina_imovel(d, i):
    s = d["site"]
    p = "../../"
    url = f"{SITE_URL}imoveis/{i['slug']}/"
    tem_preco = i.get("preco") is not None
    preco_txt = brl(i["preco"]) if tem_preco else "Sob consulta"
    desc = f"{i['resumo']} {i['bairro']}, {i['cidade']}/{i['uf']}."
    titulo = f"{i['nome']} · {i['bairro']}, {i['cidade']} | Legacy Empreendimentos"
    link_zap = zap(s["whatsapp"], f"Olá! Vi o {i['nome']} no site da Legacy Empreendimentos e quero a tabela atualizada. {url}")
    link_visita = zap(s["whatsapp"], f"Olá! Quero agendar uma visita ao decorado do {i['nome']}. {url}")

    fotos = i["fotos"]
    gal = []
    for k, f in enumerate(fotos[:3]):
        extra = f'<span class="mais">+{len(fotos) - 3} fotos</span>' if k == 2 and len(fotos) > 3 else ""
        lazy = ' loading="lazy"' if k else ""
        gal.append(f'<a href="{p}{e(f["src"])}" data-i="{k}"><img src="{p}{e(f["src"])}" alt="{e(f["legenda"])}"{lazy}>{extra}</a>')
    if len(fotos) > 1:
        gal.append(f'<button type="button" class="selo ver-todas" data-i="0">{ICONES["foto"]}&nbsp;{len(fotos)} fotos</button>')
    classe_gal = "galeria uma" if len(fotos) < 3 else "galeria"

    segs = i.get("segmentos", [])
    selos = ""
    if i.get("status") in STATUS:
        selos += f'<span class="selo">{STATUS[i["status"]]}</span>'
    if "financiamento-direto" in segs:
        selos += '<span class="selo ouro">Financiamento direto</span>'
    if "alto-padrao" in segs:
        selos += '<span class="selo ouro">Alto padrão</span>'

    fichas = [("Tipo", TIPOS.get(i["tipo"], i["tipo"]))]
    if i.get("area"):
        fichas.append(("Área privativa", faixa(i["area"], " m²")))
    if i.get("quartos"):
        fichas.append(("Quartos", faixa(i["quartos"], "", "studio")))
    fichas.append(("Vagas", i.get("vagas") or "Consulte"))
    fichas.append(("Entrega", mes_ano(i.get("entrega")) or "Consulte"))
    fichas.append(("Construtora", i["construtora"]))
    fichas_html = "".join(f'<div class="ficha"><small>{e(a)}</small><b>{e(b)}</b></div>' for a, b in fichas)

    lazer = "".join(f"<li>{e(x)}</li>" for x in i.get("lazer", []))
    bloco_lazer = f'<div class="bloco"><h2>Lazer e diferenciais</h2><ul class="lista-check">{lazer}</ul></div>' if lazer else ""
    pag = "".join(f"<li>{e(x)}</li>" for x in i.get("pagamento", []))
    bloco_pag = f'<div class="bloco"><h2>Condições de pagamento</h2><ul class="lista-check">{pag}</ul><p class="nota">{e(i.get("tabela", ""))}. Peça a simulação da sua unidade no WhatsApp.</p></div>' if pag else ""
    mapa = "https://maps.google.com/maps?q=" + urllib.parse.quote(i["endereco"]) + "&output=embed"
    fotos_js = json.dumps([{"src": p + f["src"], "legenda": f["legenda"]} for f in fotos], ensure_ascii=False)

    perfis = i.get("perfil", [])
    indicado = "".join(f'<span class="selo">{PERFIS[x]}</span>' for x in perfis if x in PERFIS)
    bloco_indicado = f'<div class="indicado">Indicado para {indicado}</div>' if indicado else ""
    bloco_roi = ""
    if "investimento" in perfis and s.get("roiUrl"):
        bloco_roi = f'<div class="roi"><a class="link-sutil" target="_blank" rel="noopener" href="{e(s["roiUrl"])}">{ICONES["grafico"]} Calcule o retorno (ROI) deste investimento ›</a></div>'

    return f"""{cabeca(titulo, desc, SITE_URL + fotos[0]['src'], url, p)}
<body class="tem-barra">
{topo(s, p)}
<main class="container">
  <div class="migalha"><a href="{p}">Início</a> › <a href="{p}#explorar">Empreendimentos</a> › {e(i['nome'])}</div>
  <div class="{classe_gal}" id="galeria" style="position:relative">{''.join(gal)}</div>
  <div class="detalhe">
    <div>
      <div class="bloco titulo-det">
        <div class="selos">{selos}</div>
        <p class="kick">{e(i['construtora'])} · {e(TIPOS.get(i['tipo'], ''))}</p>
        <h1>{e(i['nome'])}</h1>
        <div class="local">{ICONES['pin']} {e(i['endereco'])}</div>
      </div>
      <div class="bloco"><h2>Ficha do empreendimento</h2><div class="fichas">{fichas_html}</div></div>
      <div class="bloco"><h2>Sobre o empreendimento</h2><p>{e(i['descricao'])}</p></div>
      {bloco_lazer}
      {bloco_pag}
      <div class="bloco"><h2>Localização</h2><iframe class="mapa" loading="lazy" title="Mapa" src="{e(mapa)}"></iframe></div>
    </div>
    <aside class="lateral">
      <div class="bloco caixa-preco">
        <span class="rot">{'Valor de referência' if tem_preco else 'Valores'}</span>
        <div class="preco">{e(preco_txt)}</div>
        <div class="preco-nota">{e(i.get('precoNota', ''))}</div>
        <a class="btn btn-zap" target="_blank" rel="noopener" href="{e(link_zap)}">{ICONES['zap']} Quero a tabela atualizada</a>
        <a class="btn btn-sec" target="_blank" rel="noopener" href="{e(link_visita)}">Agendar visita</a>
        {bloco_indicado}
        {bloco_roi}
      </div>
    </aside>
  </div>
</main>
<div class="barra-zap"><div><b>{e(preco_txt)}</b></div><a class="btn btn-zap" target="_blank" rel="noopener" href="{e(link_zap)}">{ICONES['zap']} Tabela no WhatsApp</a></div>
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true"><button class="fechar" aria-label="Fechar">×</button><button class="ant" aria-label="Anterior">‹</button><img alt=""><p></p><button class="prox" aria-label="Próxima">›</button></div>
{rodape(s, p)}
<script>
(function(){{
  var F={fotos_js},k=0,lb=document.getElementById('lightbox'),img=lb.querySelector('img'),leg=lb.querySelector('p');
  function ver(n){{k=(n+F.length)%F.length;img.src=F[k].src;leg.textContent=(k+1)+'/'+F.length+' · '+F[k].legenda;lb.classList.add('aberto');}}
  document.querySelectorAll('#galeria [data-i]').forEach(function(a){{a.addEventListener('click',function(ev){{ev.preventDefault();ver(+a.dataset.i);}});}});
  lb.querySelector('.fechar').onclick=function(){{lb.classList.remove('aberto');}};
  lb.querySelector('.ant').onclick=function(){{ver(k-1);}};
  lb.querySelector('.prox').onclick=function(){{ver(k+1);}};
  document.addEventListener('keydown',function(ev){{if(!lb.classList.contains('aberto'))return;if(ev.key==='Escape')lb.classList.remove('aberto');if(ev.key==='ArrowLeft')ver(k-1);if(ev.key==='ArrowRight')ver(k+1);}});
  document.getElementById('form-busca').addEventListener('submit',function(ev){{ev.preventDefault();var q=document.getElementById('busca').value.trim();location.href='{p}'+(q?'?q='+encodeURIComponent(q):'')+'#explorar';}});
}})();
</script>
</body>
</html>
"""


def main():
    d = json.loads((RAIZ / "data/imoveis.json").read_text(encoding="utf-8"))
    dados = {"site": d["site"], "imoveis": d["imoveis"]}
    (RAIZ / "assets/dados.js").write_text(
        "window.DADOS = " + json.dumps(dados, ensure_ascii=False, indent=1) + ";\n"
        "window.ICONES = " + json.dumps(ICONES, ensure_ascii=False) + ";\n", encoding="utf-8")
    (RAIZ / "index.html").write_text(pagina_index(d), encoding="utf-8")
    pasta = RAIZ / "imoveis"
    if pasta.exists():
        shutil.rmtree(pasta)
    for i in d["imoveis"]:
        destino = pasta / i["slug"]
        destino.mkdir(parents=True)
        (destino / "index.html").write_text(pagina_imovel(d, i), encoding="utf-8")
    print(f"ok: {len(d['imoveis'])} imóveis, {len(d.get('embreve', []))} em breve")


if __name__ == "__main__":
    main()
