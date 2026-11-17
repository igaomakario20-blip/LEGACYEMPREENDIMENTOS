"""Acrescenta ao data/imoveis.json os empreendimentos listados num arquivo TSV
(construtora|nome|tipo|bairro|cidade|status|entrega|segmentos|pasta_drive).

Uso: python3 scripts/importar_catalogo.py caminho/catalogo.tsv
Não sobrescreve empreendimentos que já existem (mesmo slug). A pasta do Drive
não vai para o site: fica só no TSV, para consulta da equipe.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UF = {"Fortaleza": "CE", "Florianópolis": "SC", "Curitiba": "PR", "Urubici": "SC", "Anitápolis": "SC"}
TIPO_TXT = {"apartamento": "Residencial", "studio": "Studios", "casa": "Casas", "lote": "Lotes", "sala": "Salas comerciais"}
NOMES = {"City": "City Soluções Urbanas"}


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def entrada(c, nome, tipo, bairro, cidade, status, entrega, segs):
    c = NOMES.get(c, c)
    if cidade == "Goiás":
        cidade = ""
    uf = UF.get(cidade, "GO")
    onde = ", ".join(x for x in [bairro, cidade] if x)
    segs = [s for s in segs.split(",") if s]
    if status == "lancamento":
        segs.append("lancamento")
    so_invest = tipo in ("studio", "sala") or "airbnb" in segs
    perfil = ["investimento"] if so_invest else ["investimento", "moradia"]
    resumo = f"{TIPO_TXT.get(tipo, 'Empreendimento')} da {c}" + (f" em {onde}" if onde else "") + "."
    descricao = (f"{nome} é um empreendimento da {c}" + (f" em {onde}" if onde else "") +
                 ". A Equipe Legacy envia pelo WhatsApp o book completo com fotos, plantas, metragens, "
                 "tabela de preços e condições de pagamento atualizadas.")
    return {
        "slug": slug(nome), "nome": nome, "construtora": c, "cidade": cidade, "uf": uf,
        "bairro": bairro, "endereco": (onde + f"/{uf}") if cidade else "",
        "tipo": tipo, "status": status, "entrega": entrega,
        "quartos": None, "area": None, "vagas": "Consulte", "preco": None,
        "precoNota": "Tabela atualizada direto da construtora", "tabela": "",
        "segmentos": segs + ["investimento"], "destaque": False,
        "resumo": resumo, "descricao": descricao, "lazer": [], "pagamento": [],
        "fotos": [], "perfil": perfil,
    }


def main():
    arq = Path(sys.argv[1])
    caminho = RAIZ / "data/imoveis.json"
    d = json.loads(caminho.read_text(encoding="utf-8"))
    existentes = {i["slug"] for i in d["imoveis"]}
    novos = 0
    for linha in arq.read_text(encoding="utf-8").splitlines():
        if not linha.strip() or linha.startswith("#"):
            continue
        c, nome, tipo, bairro, cidade, status, entrega, segs, _pasta = linha.split("|")
        i = entrada(c, nome, tipo, bairro, cidade, status, entrega, segs)
        if i["slug"] in existentes:
            continue
        d["imoveis"].append(i)
        existentes.add(i["slug"])
        novos += 1
    d["embreve"] = [b for b in d.get("embreve", []) if b["slug"] not in existentes]
    caminho.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{novos} novos, total {len(d['imoveis'])}")


if __name__ == "__main__":
    main()
