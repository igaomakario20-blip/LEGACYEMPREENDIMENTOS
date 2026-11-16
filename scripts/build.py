#!/usr/bin/env python3
"""Gera o site a partir de data/imoveis.json.

Saídas:
  assets/dados.js            dados usados pela página de busca
  index.html                 página de busca (segmentos + filtros + simulador)
  imoveis/<slug>/index.html  uma página por empreendimento, com prévia para WhatsApp

Uso: python3 scripts/build.py
"""
import html
import json
import shutil
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITE_URL = "https://igaomakario20-blip.github.io/LEGACYEMPREENDIMENTOS/"

TIPOS = {"apartamento": "Apartamento", "studio": "Studio", "casa": "Casa", "lote": "Lote", "sala": "Sala comercial"}
STATUS = {"lancamento": "Lançamento", "em-obra": "Em obra", "entregue": "Pronto para morar"}
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

ICONE_ZAP = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 '
             '14.2c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.3-.7-2.8-1.1-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.9s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 '
             '2c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.1 1 2.1 1.3 2.4 1.5.3.1.5.1.7-.1l.9-1.1c.2-.3.4-.2.7-.1l2 .9c.3.1.5.2.5.3.1.2.1.7-.1 1.3z"/></svg>')

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
<meta property="og:type" content="website">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:image" content="{e(imagem)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefixo}assets/estilo.css">
</head>"""


def topo(c, prefixo):
    return f"""<header class="topo"><div class="container">
  <a class="marca" href="{prefixo}"><b>{e(c['nome'])} Imóveis</b><small>{e(c['empresa'])}</small></a>
  <form class="busca" id="form-busca" action="{prefixo}" role="search">
    <input id="busca" name="q" type="search" placeholder="Buscar por bairro, empreendimento ou construtora" aria-label="Buscar">
    <button type="submit">Buscar</button>
  </form>
  <a class="btn-zap-topo" target="_blank" rel="noopener" href="{e(zap(c['whatsapp'], 'Olá Igor! Vi seu site de imóveis e quero mais informações.'))}">{ICONE_ZAP}<span>{e(c['whatsappTexto'])}</span></a>
</div></header>"""


def rodape(c):
    return f"""<footer class="rodape-site"><div class="container">
  <div><b>{e(c['nome'])}</b> · {e(c['titulo'])}<br>{e(c['empresa'])} · {e(c['creci'])}</div>
  <div>Preços e condições conforme a tabela de cada construtora e sujeitos a alteração sem aviso.<br>Imagens ilustrativas fornecidas pelas construtoras.</div>
</div></footer>"""


def pagina_index(d):
    c = d["corretor"]
    titulo = f"{c['nome']} Imóveis · lançamentos e oportunidades em Goiânia"
    desc = f"Apartamentos, studios, casas e lançamentos selecionados por {c['nome']}, {c['titulo'].lower()}. Filtre por bairro, preço e quartos e fale direto no WhatsApp."
    capa = d["imoveis"][0]["fotos"][0]["src"] if d["imoveis"] else c["foto"]
    return f"""{cabeca(titulo, desc, SITE_URL + capa, SITE_URL, '')}
<body>
{topo(c, '')}
<nav class="segmentos" aria-label="Segmentos"><div class="container" id="segmentos"></div></nav>

<section class="hero"><div class="container">
  <div>
    <h1>Encontre seu imóvel ou seu próximo <em>investimento</em> em Goiânia</h1>
    <p>Lançamentos, prontos para morar e oportunidades de renda das melhores construtoras, com atendimento direto comigo.</p>
  </div>
  <div class="corretor-mini"><img src="{e(c['foto'])}" alt="{e(c['nome'])}"><div><b>{e(c['nome'])}</b><small>{e(c['titulo'])}</small><small>{e(c['creci'])}</small></div></div>
</div></section>

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
      <button type="button" class="btn btn-ver" id="ver-resultados">Ver resultados</button>
    </aside>
    <section>
      <div class="resultado-topo">
        <h2 id="titulo-resultado">Imóveis à venda</h2>
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
    <p style="margin-top:16px"><a class="btn btn-zap" id="s-zap" target="_blank" rel="noopener" href="#">{ICONE_ZAP} Quero opções nessa faixa</a></p>
  </div></section>

  <section id="painel-sobre" class="lista-layout" hidden><div></div><div class="painel">
    <div class="sobre"><img src="{e(c['foto'])}" alt="{e(c['nome'])}"><div>
      <h2>{e(c['nome'])}</h2>
      <p class="sub">{e(c['titulo'])}<br>{e(c['empresa'])} · {e(c['creci'])}</p>
      <p>Trabalho com dezenas de construtoras de Goiânia e região. Te ajudo a escolher o imóvel certo para morar ou investir, comparo condições de pagamento e acompanho tudo até a entrega das chaves.</p>
      <p style="margin-top:16px"><a class="btn btn-zap" data-zap="Olá Igor! Vi seu site e quero conversar sobre imóveis." target="_blank" rel="noopener" href="#">{ICONE_ZAP} Falar no WhatsApp</a></p>
    </div></div>
  </div></section>
</main>
{rodape(c)}
<script src="assets/dados.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
"""


def pagina_imovel(d, i):
    c = d["corretor"]
    p = "../../"
    url = f"{SITE_URL}imoveis/{i['slug']}/"
    preco_txt = brl(i["preco"]) if i.get("preco") is not None else "Sob consulta"
    desc = f"{i['resumo']} {i['bairro']}, {i['cidade']}/{i['uf']}."
    titulo = f"{i['nome']} · {i['bairro']}, {i['cidade']}"
    msg = f"Olá Igor! Vi o {i['nome']} no seu site e quero saber mais. {url}"
    link_zap = zap(c["whatsapp"], msg)

    fotos = i["fotos"]
    mostrar = fotos[:3]
    gal = []
    for k, f in enumerate(mostrar):
        extra = f'<span class="mais">+{len(fotos) - 3} fotos</span>' if k == 2 and len(fotos) > 3 else ""
        lazy = ' loading="lazy"' if k else ""
        gal.append(f'<a href="{p}{e(f["src"])}" data-i="{k}"><img src="{p}{e(f["src"])}" alt="{e(f["legenda"])}"{lazy}>{extra}</a>')
    classe_gal = "galeria uma" if len(fotos) < 3 else "galeria"

    selos = ""
    if i.get("status") in STATUS:
        selos += f'<span class="selo">{STATUS[i["status"]]}</span>'
    if "financiamento-direto" in i.get("segmentos", []):
        selos += '<span class="selo ouro">Financiamento direto</span>'
    if "alto-padrao" in i.get("segmentos", []):
        selos += '<span class="selo ouro">Alto padrão</span>'
    if "investimento" in i.get("segmentos", []):
        selos += '<span class="selo">Bom para investir</span>'

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
    pag = "".join(f"<li>{e(x)}</li>" for x in i.get("pagamento", []))
    bloco_pag = f'<div class="bloco"><h2>Condições de pagamento</h2><ul class="lista-check">{pag}</ul><p class="nota">{e(i.get("tabela", ""))}. Peça a simulação da sua unidade no WhatsApp.</p></div>' if pag else ""
    mapa = "https://maps.google.com/maps?q=" + urllib.parse.quote(i["endereco"]) + "&output=embed"
    fotos_js = json.dumps([{"src": p + f["src"], "legenda": f["legenda"]} for f in fotos], ensure_ascii=False)

    return f"""{cabeca(titulo, desc, SITE_URL + fotos[0]['src'], url, p)}
<body class="tem-barra">
{topo(c, p)}
<main class="container">
  <div class="migalha"><a href="{p}">Início</a> › <a href="{p}#{'apartamentos' if i['tipo'] == 'apartamento' else 'todos'}">{e(TIPOS.get(i['tipo'], 'Imóveis'))}</a> › {e(i['nome'])}</div>
  <div class="{classe_gal}" id="galeria">{''.join(gal)}</div>
  <div class="detalhe">
    <div>
      <div class="bloco titulo-det">
        <div class="selos">{selos}</div>
        <h1>{e(i['nome'])}</h1>
        <div class="local">{e(i['endereco'])}</div>
      </div>
      <div class="bloco"><h2>Ficha do imóvel</h2><div class="fichas">{fichas_html}</div></div>
      <div class="bloco"><h2>Sobre o empreendimento</h2><p>{e(i['descricao'])}</p></div>
      <div class="bloco"><h2>Lazer e diferenciais</h2><ul class="lista-check">{lazer}</ul></div>
      {bloco_pag}
      <div class="bloco"><h2>Localização</h2><iframe class="mapa" loading="lazy" title="Mapa" src="{e(mapa)}"></iframe></div>
    </div>
    <aside class="lateral">
      <div class="bloco caixa-preco">
        <div class="preco">{e(preco_txt)}</div>
        <div class="preco-nota">{e(i.get('precoNota', ''))}</div>
        <a class="btn btn-zap" target="_blank" rel="noopener" href="{e(link_zap)}">{ICONE_ZAP} Quero a tabela atualizada</a>
        <a class="btn btn-sec" target="_blank" rel="noopener" href="{e(zap(c['whatsapp'], f'Olá Igor! Quero agendar uma visita ao decorado do {i["nome"]}.'))}">Agendar visita</a>
        <div class="caixa-corretor"><img src="{p}{e(c['foto'])}" alt="{e(c['nome'])}"><div><b>{e(c['nome'])}</b><small>{e(c['titulo'])}</small><small>{e(c['creci'])}</small></div></div>
      </div>
    </aside>
  </div>
</main>
<div class="barra-zap"><div><b>{e(preco_txt)}</b></div><a class="btn btn-zap" target="_blank" rel="noopener" href="{e(link_zap)}">{ICONE_ZAP} WhatsApp</a></div>
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true"><button class="fechar" aria-label="Fechar">×</button><button class="ant" aria-label="Anterior">‹</button><img alt=""><p></p><button class="prox" aria-label="Próxima">›</button></div>
{rodape(c)}
<script>
(function(){{
  var F={fotos_js},k=0,lb=document.getElementById('lightbox'),img=lb.querySelector('img'),leg=lb.querySelector('p');
  function ver(n){{k=(n+F.length)%F.length;img.src=F[k].src;leg.textContent=(k+1)+'/'+F.length+' · '+F[k].legenda;lb.classList.add('aberto');}}
  document.querySelectorAll('#galeria a').forEach(function(a){{a.addEventListener('click',function(ev){{ev.preventDefault();ver(+a.dataset.i);}});}});
  lb.querySelector('.fechar').onclick=function(){{lb.classList.remove('aberto');}};
  lb.querySelector('.ant').onclick=function(){{ver(k-1);}};
  lb.querySelector('.prox').onclick=function(){{ver(k+1);}};
  document.addEventListener('keydown',function(ev){{if(!lb.classList.contains('aberto'))return;if(ev.key==='Escape')lb.classList.remove('aberto');if(ev.key==='ArrowLeft')ver(k-1);if(ev.key==='ArrowRight')ver(k+1);}});
  document.getElementById('form-busca').addEventListener('submit',function(ev){{ev.preventDefault();location.href='{p}#todos';}});
}})();
</script>
</body>
</html>
"""


def main():
    d = json.loads((RAIZ / "data/imoveis.json").read_text(encoding="utf-8"))
    (RAIZ / "assets/dados.js").write_text("window.DADOS = " + json.dumps(d, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    (RAIZ / "index.html").write_text(pagina_index(d), encoding="utf-8")
    pasta = RAIZ / "imoveis"
    if pasta.exists():
        shutil.rmtree(pasta)
    for i in d["imoveis"]:
        destino = pasta / i["slug"]
        destino.mkdir(parents=True)
        (destino / "index.html").write_text(pagina_imovel(d, i), encoding="utf-8")
    print(f"ok: {len(d['imoveis'])} imóveis")


if __name__ == "__main__":
    main()
