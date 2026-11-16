# Legacy Empreendimentos

Site de vendas de imóveis no estilo classificados: segmentos no topo, filtros na lateral, um card por empreendimento e uma página própria para cada um, com botão de WhatsApp e prévia com foto quando o link é enviado.

## Como funciona

- `data/imoveis.json`: catálogo. Uma entrada por empreendimento (dados, segmentos, fotos).
- `img/<slug>/`: fotos já reduzidas em WebP (até 1600 px).
- `scripts/build.py`: gera `index.html`, `assets/dados.js` e `imoveis/<slug>/index.html` a partir do catálogo.
- `assets/estilo.css` e `assets/app.js`: visual, filtros, segmentos e simulador.

## Adicionar ou mudar um imóvel

1. Edite `data/imoveis.json`.
2. Coloque as fotos em `img/<slug>/`.
3. Rode `python3 scripts/build.py`.
4. Faça commit e push. O GitHub Pages publica sozinho.

Campos de segmento aceitos: `lancamento`, `financiamento-direto`, `mcmv`, `investimento`, `alto-padrao`, `aluguel`.
Status: `lancamento`, `em-obra`, `entregue` (vazio = consulte). "Próximo à entrega" usa `em-obra` com `entrega` em até 12 meses.

## Ver localmente

```
python3 -m http.server 8000
```
e abra http://localhost:8000

## Coleções, perfil e "em breve"

- `site`: nome, WhatsApp, link do simulador de ROI (`roiUrl`) e texto do rodapé.
- `perfil` de cada imóvel: `investimento` e/ou `moradia` (alimenta o filtro "Seu objetivo").
- `colecoes`: blocos em destaque na página inicial; `itens` lista slugs de `imoveis` ou de `embreve`.
- `embreve`: empreendimentos ainda sem material; aparecem nas coleções com o botão "Pedir apresentação" (WhatsApp). Quando o material chegar, mova para `imoveis` com o mesmo slug.
