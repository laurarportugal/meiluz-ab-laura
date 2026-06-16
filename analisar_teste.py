#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import csv
import argparse
import unicodedata
import math
from datetime import datetime, date


def _strip_accents(s):
    if s is None:
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def _norm_coluna(s):
    base = _strip_accents(s)
    base = "".join(c if (c.isascii() and (c.isalpha() or c == " ")) else " " for c in base)
    return " ".join(base.split())


PALAVRAS_CHAVE = [
    ("variante", ["grupo", "variante"]),
    ("comissao", ["comiss"]),
    ("cashback", ["cashback"]),
    ("vendas", ["vendas", "gmv"]),
    ("compradores", ["comprador"]),
    ("parceiro", ["parceiro"]),
    ("data", ["data", "date"]),
]

COLUNAS_CANONICAS = {
    "data": "data",
    "grupos de usuarios": "variante",
    "grupo de usuarios": "variante",
    "grupo": "variante",
    "variante": "variante",
    "parceiro": "parceiro",
    "compradores": "compradores",
    "comissao": "comissao",
    "cashback": "cashback",
    "vendas totais": "vendas",
    "vendas": "vendas",
    "gmv": "vendas",
}


def _casar_coluna(nome):
    norm = _norm_coluna(nome)
    if not norm:
        return None
    if norm in COLUNAS_CANONICAS:
        return COLUNAS_CANONICAS[norm]
    for canonica, chaves in PALAVRAS_CHAVE:
        if any(k in norm for k in chaves):
            return canonica
    return None


def parse_dinheiro(valor):
    if valor is None:
        return None
    s = str(valor).strip()
    if s == "":
        return None
    s = s.replace("R$", "").replace("r$", "").strip().replace(" ", "")
    if s == "":
        return None
    neg = s.startswith("-")
    s = s.lstrip("-")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(".", "")
    try:
        n = float(s)
    except ValueError:
        return None
    return -n if neg else n


def parse_int(valor):
    if valor is None:
        return None
    s = str(valor).strip()
    if s == "":
        return None
    try:
        return int(float(s.replace(".", "").replace(",", ".")))
    except ValueError:
        return None


def parse_data(valor):
    s = str(valor).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def ler_dataset(caminho):
    avisos = []
    conteudo = None
    for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            with open(caminho, "r", encoding=enc, newline="") as f:
                conteudo = f.read()
            break
        except (UnicodeDecodeError, LookupError):
            continue
    if conteudo is None:
        raise SystemExit(f"ERRO: nao consegui ler o arquivo {caminho}")

    reader = csv.reader(conteudo.splitlines())
    linhas_raw = list(reader)
    if not linhas_raw:
        raise SystemExit("ERRO: arquivo vazio.")

    header = linhas_raw[0]
    idx_para_chave = {}
    for i, nome in enumerate(header):
        canonica = _casar_coluna(nome)
        if canonica:
            idx_para_chave[i] = canonica

    obrigatorias = {"data", "variante", "compradores", "comissao", "cashback", "vendas"}
    encontradas = set(idx_para_chave.values())
    faltando = obrigatorias - encontradas
    if faltando:
        raise SystemExit(f"ERRO: colunas obrigatorias nao encontradas: {faltando}. Cabecalho: {header}")

    linhas = []
    descartadas = 0
    for n, raw in enumerate(linhas_raw[1:], start=2):
        if not any(c.strip() for c in raw):
            continue
        reg = {}
        for i, valor in enumerate(raw):
            chave = idx_para_chave.get(i)
            if not chave:
                continue
            reg[chave] = valor
        reg_parsed = {
            "data": parse_data(reg.get("data")),
            "variante": (reg.get("variante") or "").strip(),
            "parceiro": (reg.get("parceiro") or "").strip(),
            "compradores": parse_int(reg.get("compradores")),
            "comissao": parse_dinheiro(reg.get("comissao")),
            "cashback": parse_dinheiro(reg.get("cashback")),
            "vendas": parse_dinheiro(reg.get("vendas")),
        }
        if reg_parsed["data"] is None or not reg_parsed["variante"]:
            descartadas += 1
            continue
        if reg_parsed["comissao"] is None or reg_parsed["cashback"] is None:
            descartadas += 1
            continue
        linhas.append(reg_parsed)

    if descartadas:
        avisos.append(f"{descartadas} linha(s) descartada(s) por dados invalidos.")
    if not linhas:
        raise SystemExit("ERRO: nenhuma linha valida apos o parsing.")
    return linhas, avisos


def media(xs):
    return sum(xs) / len(xs) if xs else 0.0


def desvio_padrao_amostral(xs):
    n = len(xs)
    if n < 2:
        return 0.0
    m = media(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def _gammln(xx):
    cof = [76.18009172947146, -86.50532032941677, 24.01409824083091,
           -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5]
    x = xx
    y = xx
    tmp = x + 5.5
    tmp -= (x + 0.5) * math.log(tmp)
    ser = 1.000000000190015
    for c in cof:
        y += 1
        ser += c / y
    return -tmp + math.log(2.5066282746310005 * ser / x)


def _betacf(a, b, x):
    MAXIT, EPS, FPMIN = 200, 3.0e-9, 1.0e-30
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < EPS:
            break
    return h


def _betai(a, b, x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(_gammln(a + b) - _gammln(a) - _gammln(b)
                  + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def p_valor_t(t, df):
    if df <= 0:
        return float("nan")
    return _betai(df / 2.0, 0.5, df / (df + t * t))


def teste_t_pareado(serie_a, serie_b):
    difs = [a - b for a, b in zip(serie_a, serie_b)]
    n = len(difs)
    if n < 2:
        return {"t": float("nan"), "df": 0, "p": float("nan"),
                "diff_media": media(difs) if difs else 0.0, "n": n}
    m = media(difs)
    sd = desvio_padrao_amostral(difs)
    if sd == 0:
        return {"t": float("inf") if m != 0 else 0.0, "df": n - 1,
                "p": 0.0 if m != 0 else 1.0, "diff_media": m, "n": n}
    se = sd / math.sqrt(n)
    t = m / se
    df = n - 1
    return {"t": t, "df": df, "p": p_valor_t(t, df), "diff_media": m, "n": n}


def agregar_por_variante(linhas):
    variantes = {}
    for r in linhas:
        v = r["variante"]
        d = variantes.setdefault(v, {
            "variante": v, "dias": 0,
            "compradores": 0, "comissao": 0.0, "cashback": 0.0, "vendas": 0.0,
            "serie_margem_dia": {},
        })
        comp = r["compradores"] or 0
        com = r["comissao"] or 0.0
        cb = r["cashback"] or 0.0
        ven = r["vendas"] or 0.0
        d["dias"] += 1
        d["compradores"] += comp
        d["comissao"] += com
        d["cashback"] += cb
        d["vendas"] += ven
        d["serie_margem_dia"][r["data"]] = com - cb

    for v, d in variantes.items():
        d["margem_liquida"] = d["comissao"] - d["cashback"]
        d["take_rate"] = d["comissao"] / d["vendas"] if d["vendas"] else 0.0
        d["cashback_rate"] = d["cashback"] / d["vendas"] if d["vendas"] else 0.0
        d["margem_rate"] = d["margem_liquida"] / d["vendas"] if d["vendas"] else 0.0
        d["margem_por_comprador"] = d["margem_liquida"] / d["compradores"] if d["compradores"] else 0.0
        d["ticket_medio"] = d["vendas"] / d["compradores"] if d["compradores"] else 0.0
        d["roi_cashback"] = d["margem_liquida"] / d["cashback"] if d["cashback"] else float("inf")
    return variantes


def checar_qualidade(linhas, variantes):
    avisos = []
    invalidas = set()

    periodos = {}
    for v, d in variantes.items():
        datas = list(d["serie_margem_dia"].keys())
        periodos[v] = (min(datas), max(datas), len(datas))

    for v, d in variantes.items():
        dias_iguais = 0
        total = 0
        for r in linhas:
            if r["variante"] != v:
                continue
            total += 1
            if r["comissao"] is not None and r["cashback"] is not None \
                    and abs(r["comissao"] - r["cashback"]) < 1e-6:
                dias_iguais += 1
        if total and dias_iguais / total > 0.8:
            invalidas.add(v)
            avisos.append(
                f"[CRITICO] {v}: cashback == comissao em {dias_iguais}/{total} dias "
                f"(margem zero). Suspeita de dado corrompido. Variante EXCLUIDA da decisao."
            )

    for v, d in variantes.items():
        if v in invalidas:
            continue
        dias_neg = sum(
            1 for r in linhas
            if r["variante"] == v and r["comissao"] is not None
            and r["cashback"] is not None and r["cashback"] > r["comissao"]
        )
        if dias_neg:
            avisos.append(f"[ATENCAO] {v}: {dias_neg} dia(s) com cashback > comissao (margem negativa).")
        if d["margem_liquida"] <= 0:
            invalidas.add(v)
            avisos.append(f"[CRITICO] {v}: margem liquida total <= 0. Variante excluida da decisao.")

    n_var = len(variantes)
    if n_var < 2:
        avisos.append(f"[CRITICO] Apenas {n_var} variante valida — sem A/B comparavel.")
    elif n_var == 2:
        avisos.append("[INFO] Teste com 2 variantes (A/B simples).")

    inicios = {p[0] for p in periodos.values()}
    fins = {p[1] for p in periodos.values()}
    if len(inicios) > 1 or len(fins) > 1:
        avisos.append("[ATENCAO] Variantes com janelas de data diferentes — comparacao pode estar enviesada.")

    max_dias = max((p[2] for p in periodos.values()), default=0)
    if max_dias < 14:
        avisos.append(f"[ATENCAO] Amostra curta ({max_dias} dias). Resultado pode nao ser confiavel.")

    for v, d in variantes.items():
        serie = [d["serie_margem_dia"][k] for k in sorted(d["serie_margem_dia"])]
        if len(serie) >= 6:
            base = media(serie[:-3]) if len(serie) > 3 else media(serie)
            fim = media(serie[-3:])
            if base > 0 and fim < 0.5 * base:
                avisos.append(f"[ATENCAO] {v}: margem dos ultimos 3 dias caiu >50% — possivel coleta truncada.")

    for v, d in variantes.items():
        comp = [r["compradores"] for r in linhas if r["variante"] == v and r["compradores"] is not None]
        if len(comp) >= 5:
            m = media(comp)
            sd = desvio_padrao_amostral(comp)
            picos = [c for c in comp if sd and abs(c - m) > 4 * sd]
            if picos:
                avisos.append(f"[INFO] {v}: {len(picos)} dia(s) com pico de compradores >4 desvios.")

    return avisos, invalidas


def decidir(variantes, invalidas):
    validas = {v: d for v, d in variantes.items() if v not in invalidas}
    resultado = {"vencedora": None, "vice": None, "teste": None,
                 "inconclusivo": False, "motivo": "", "validas": validas}

    if len(validas) == 0:
        resultado["inconclusivo"] = True
        resultado["motivo"] = "Nenhuma variante valida apos checagens de qualidade."
        return resultado

    ordenadas = sorted(validas.values(), key=lambda d: d["margem_liquida"], reverse=True)
    vencedora = ordenadas[0]
    resultado["vencedora"] = vencedora

    if len(validas) == 1:
        resultado["inconclusivo"] = True
        resultado["motivo"] = "Apenas 1 variante valida — sem comparativo A/B confiavel. Recomendacao provisoria."
        return resultado

    vice = ordenadas[1]
    resultado["vice"] = vice

    datas_comuns = sorted(set(vencedora["serie_margem_dia"]) & set(vice["serie_margem_dia"]))
    serie_venc = [vencedora["serie_margem_dia"][dt] for dt in datas_comuns]
    serie_vice = [vice["serie_margem_dia"][dt] for dt in datas_comuns]
    teste = teste_t_pareado(serie_venc, serie_vice)
    resultado["teste"] = teste

    uplift = (vencedora["margem_liquida"] - vice["margem_liquida"]) / vice["margem_liquida"] \
        if vice["margem_liquida"] else float("inf")
    resultado["uplift_vs_vice"] = uplift

    p = teste["p"]
    if p == p and p < 0.05:
        resultado["motivo"] = (
            f"{vencedora['variante']} tem a maior margem liquida e a diferenca diaria "
            f"vs {vice['variante']} e estatisticamente significativa (p={p:.4f})."
        )
    else:
        resultado["inconclusivo"] = True
        resultado["motivo"] = (
            f"{vencedora['variante']} tem a maior margem liquida, porem a diferenca "
            f"vs {vice['variante']} NAO e estatisticamente significativa (p={p:.4f}). "
            f"Considere estender o teste."
        )
    return resultado


def mil(n):
    if n is None:
        return "-"
    return f"{int(round(n)):,}".replace(",", ".")


def brl(x):
    if x is None:
        return "-"
    if x == float("inf"):
        return "inf"
    return "R$ " + mil(x)


def pct(x):
    return f"{x*100:.1f}%"


def montar_relatorio(meta, variantes, invalidas, avisos, decisao):
    L = []
    p = L.append
    parceiro = meta["parceiro"]
    p(f"# Relatorio de Teste A/B de Cashback — {parceiro}")
    p("")
    p(f"- **Teste:** {meta['nome']}")
    p(f"- **Periodo:** {meta['periodo_ini']} a {meta['periodo_fim']} ({meta['n_dias']} dias)")
    p(f"- **Variantes:** {meta['n_variantes']}")
    p(f"- **Metrica de decisao:** Margem liquida (comissao - cashback)")
    p(f"- **Gerado em:** {meta['gerado_em']}")
    p("")
    p("## Recomendacao")
    p("")
    if decisao["vencedora"] is None:
        p("> **Nao foi possivel recomendar uma variante.** " + decisao["motivo"])
    else:
        venc = decisao["vencedora"]
        tag = "INCONCLUSIVO" if decisao["inconclusivo"] else "ESCALAR"
        p(f"> **[{tag}] Escalar {venc['variante']} para 100% do trafego.**")
        p("")
        p(decisao["motivo"])
        if decisao.get("vice") and decisao.get("uplift_vs_vice") is not None:
            up = decisao["uplift_vs_vice"]
            up_s = f"{up*100:+.1f}%" if up != float("inf") else "+inf"
            p("")
            p(f"Margem liquida {up_s} vs vice ({decisao['vice']['variante']}).")
    p("")
    p("## Comparativo entre variantes")
    p("")
    p("| Variante | Compradores | GMV (vendas) | Comissao | Cashback | Margem liquida | Margem % GMV | Cashback % GMV | Margem/comprador |")
    p("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for v in sorted(variantes):
        d = variantes[v]
        flag = " ⚠️" if v in invalidas else ""
        p(f"| {v}{flag} | {mil(d['compradores'])} | {brl(d['vendas'])} | {brl(d['comissao'])} | "
          f"{brl(d['cashback'])} | {brl(d['margem_liquida'])} | {pct(d['margem_rate'])} | "
          f"{pct(d['cashback_rate'])} | {brl(d['margem_por_comprador'])} |")
    p("")
    p("⚠️ = variante com problema de qualidade de dados; excluida da decisao.")
    p("")
    p("## Leitura de negocio")
    p("")
    validas = decisao["validas"]
    if len(validas) >= 2:
        ord_cb = sorted(validas.values(), key=lambda d: d["cashback_rate"])
        menor, maior = ord_cb[0], ord_cb[-1]
        p(f"- Faixa de cashback testada: de **{pct(menor['cashback_rate'])}** ({menor['variante']}) "
          f"a **{pct(maior['cashback_rate'])}** ({maior['variante']}) sobre o GMV.")
        p(f"- {maior['variante']} (mais cashback) gerou "
          f"{'mais' if maior['compradores'] > menor['compradores'] else 'menos'} compradores "
          f"({mil(maior['compradores'])} vs {mil(menor['compradores'])}) e "
          f"{'mais' if maior['vendas'] > menor['vendas'] else 'menos'} GMV, "
          f"mas margem liquida de {brl(maior['margem_liquida'])} "
          f"vs {brl(menor['margem_liquida'])}.")
        p(f"- Aumentar cashback {'NAO se' if menor['margem_liquida'] >= maior['margem_liquida'] else 'se'} "
          f"pagou em margem liquida neste teste.")
    else:
        p(f"- Apenas o {list(validas.keys())[0] if validas else '—'} e valido para analise.")
        if validas:
            v = list(validas.values())[0]
            p(f"  Margem liquida: {brl(v['margem_liquida'])} | Margem % GMV: {pct(v['margem_rate'])} | "
              f"Margem/comprador: {brl(v['margem_por_comprador'])}.")
        p("- Acionar engenharia de dados para investigar as variantes excluidas antes de tomar decisao final.")
    if decisao.get("teste"):
        t = decisao["teste"]
        p(f"- Significancia (t pareado por dia, vencedora vs vice): "
          f"t={t['t']:.2f}, df={t['df']}, p={t['p']:.4f}, n={t['n']} dias.")
    p("")
    p("> **Premissa-chave:** comparacao de margem total assume split de trafego igual entre variantes. "
      "Em caso de duvida, use margem/comprador e margem % GMV.")
    p("")
    p("## Qualidade de dados e ressalvas")
    p("")
    if avisos:
        for a in avisos:
            p(f"- {a}")
    else:
        p("- Nenhum problema relevante detectado.")
    p("")
    p("---")
    p(f"*Relatorio gerado automaticamente por `analisar_teste.py` em {meta['gerado_em']}.*")
    return "\n".join(L)


def registrar_planilha(caminho_csv, meta, variantes, invalidas, decisao):
    header = ["data_analise", "nome_teste", "parceiro", "periodo", "n_variantes",
              "descricao", "metrica_decisao", "resultado", "decisao",
              "significancia_p", "ressalvas"]

    venc = decisao["vencedora"]
    if venc is None:
        resultado = "Sem variante valida"
        decisao_txt = "Nao escalar — revisar dados"
    else:
        resultado = f"Vencedora {venc['variante']}: margem liq. {brl(venc['margem_liquida'])}"
        if decisao.get("vice"):
            resultado += f" vs {decisao['vice']['variante']} {brl(decisao['vice']['margem_liquida'])}"
        prefixo = "INCONCLUSIVO — " if decisao["inconclusivo"] else ""
        decisao_txt = f"{prefixo}Escalar {venc['variante']} para 100%"

    p_val = ""
    if decisao.get("teste") and decisao["teste"]["p"] == decisao["teste"]["p"]:
        p_val = f"{decisao['teste']['p']:.4f}"

    ressalvas = "; ".join(a for a in meta["avisos"] if a.startswith("[CRITICO]") or a.startswith("[ATENCAO]"))
    if not ressalvas:
        ressalvas = "Sem ressalvas relevantes"

    linha = [
        meta["gerado_em"], meta["nome"], meta["parceiro"],
        f"{meta['periodo_ini']} a {meta['periodo_fim']}", str(meta["n_variantes"]),
        meta["descricao"], "Margem liquida (comissao - cashback)",
        resultado, decisao_txt, p_val, ressalvas,
    ]

    existe = os.path.exists(caminho_csv)
    with open(caminho_csv, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(header)
        w.writerow(linha)


def main():
    ap = argparse.ArgumentParser(description="Analisa um teste A/B de cashback.")
    ap.add_argument("dataset", help="Caminho do CSV do teste A/B.")
    ap.add_argument("--nome", help="Nome do teste.")
    ap.add_argument("--descricao", help="Descricao do teste para a planilha.")
    ap.add_argument("--planilha", default="planilha_acompanhamento.csv")
    ap.add_argument("--saida", default="relatorios")
    ap.add_argument("--hoje", help="Data da analise YYYY-MM-DD (default: hoje).")
    args = ap.parse_args()

    if not os.path.exists(args.dataset):
        raise SystemExit(f"ERRO: arquivo nao encontrado: {args.dataset}")

    linhas, avisos_leitura = ler_dataset(args.dataset)
    variantes = agregar_por_variante(linhas)
    avisos_dq, invalidas = checar_qualidade(linhas, variantes)
    avisos = avisos_leitura + avisos_dq
    decisao = decidir(variantes, invalidas)

    parceiro = next((r["parceiro"] for r in linhas if r["parceiro"]), "Parceiro ?")
    todas_datas = [r["data"] for r in linhas]
    nome = args.nome or f"Cashback {parceiro}"
    hoje = args.hoje or date.today().isoformat()
    descricao = args.descricao or (
        f"Teste A/B de % de cashback no {parceiro}, comparando {len(variantes)} variantes.")
    meta = {
        "nome": nome, "parceiro": parceiro, "descricao": descricao,
        "periodo_ini": min(todas_datas).isoformat(),
        "periodo_fim": max(todas_datas).isoformat(),
        "n_dias": len(set(todas_datas)),
        "n_variantes": len(variantes),
        "gerado_em": hoje, "avisos": avisos,
    }

    relatorio = montar_relatorio(meta, variantes, invalidas, avisos, decisao)

    os.makedirs(args.saida, exist_ok=True)
    slug = _strip_accents(parceiro).replace(" ", "_") or "teste"
    caminho_rel = os.path.join(args.saida, f"relatorio_{slug}.md")
    with open(caminho_rel, "w", encoding="utf-8") as f:
        f.write(relatorio)

    registrar_planilha(args.planilha, meta, variantes, invalidas, decisao)

    print(relatorio)
    print("\n" + "=" * 70)
    print(f"Relatorio salvo em:  {caminho_rel}")
    print(f"Planilha atualizada: {args.planilha}")
    print("=" * 70)


if __name__ == "__main__":
    main()