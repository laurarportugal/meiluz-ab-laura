# Relatorio de Teste A/B de Cashback — Parceiro B

- **Teste:** Cashback Parceiro B
- **Periodo:** 2011-05-01 a 2011-06-30 (61 dias)
- **Variantes:** 3
- **Metrica de decisao:** Margem liquida (comissao - cashback)
- **Gerado em:** 2026-06-16

## Recomendacao

> **[ESCALAR] Escalar Grupo 1 para 100% do trafego.**

Grupo 1 tem a maior margem liquida e a diferenca diaria vs Grupo 2 e estatisticamente significativa (p=0.0000).

Margem liquida +100.2% vs vice (Grupo 2).

## Comparativo entre variantes

| Variante | Compradores | GMV (vendas) | Comissao | Cashback | Margem liquida | Margem % GMV | Cashback % GMV | Margem/comprador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Grupo 1 | 7.990 | R$ 4.093.818 | R$ 450.321 | R$ 163.751 | R$ 286.570 | 7.0% | 4.0% | R$ 36 |
| Grupo 2 | 5.452 | R$ 2.863.019 | R$ 314.935 | R$ 171.778 | R$ 143.157 | 5.0% | 6.0% | R$ 26 |
| Grupo 3 | 5.029 | R$ 2.629.963 | R$ 289.290 | R$ 236.697 | R$ 52.593 | 2.0% | 9.0% | R$ 10 |

⚠️ = variante com problema de qualidade de dados; excluida da decisao.

## Leitura de negocio

- Faixa de cashback testada: de **4.0%** (Grupo 1) a **9.0%** (Grupo 3) sobre o GMV.
- Grupo 3 (mais cashback) gerou menos compradores (5.029 vs 7.990) e menos GMV, mas margem liquida de R$ 52.593 vs R$ 286.570.
- Aumentar cashback NAO se pagou em margem liquida neste teste.
- Significancia (t pareado por dia, vencedora vs vice): t=15.39, df=60, p=0.0000, n=61 dias.

> **Premissa-chave:** comparacao de margem total assume split de trafego igual entre variantes. Em caso de duvida, use margem/comprador e margem % GMV.

## Qualidade de dados e ressalvas

- [INFO] Grupo 1: 1 dia(s) com pico de compradores >4 desvios.
- [INFO] Grupo 2: 2 dia(s) com pico de compradores >4 desvios.
- [INFO] Grupo 3: 2 dia(s) com pico de compradores >4 desvios.

---
*Relatorio gerado automaticamente por `analisar_teste.py` em 2026-06-16.*