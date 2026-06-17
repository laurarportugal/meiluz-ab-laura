# Relatorio de Teste A/B de Cashback — Parceiro A

- **Teste:** Cashback Parceiro A
- **Periodo:** 2011-01-01 a 2011-04-02 (92 dias)
- **Variantes:** 3
- **Metrica de decisao:** Margem liquida (comissao - cashback)
- **Gerado em:** 2026-06-17

## Recomendacao

> **[ESCALAR] Escalar Grupo 1 para 100% do trafego.**

Grupo 1 tem a maior margem liquida e a diferenca diaria vs Grupo 2 e estatisticamente significativa (p=0.0000).

Margem liquida +13.2% vs vice (Grupo 2).

## Comparativo entre variantes

| Variante | Compradores | GMV (vendas) | Comissao | Cashback | Margem liquida | Margem % GMV | Cashback % GMV | Margem/comprador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Grupo 1 | 9.633 | R$ 5.605.173 | R$ 638.135 | R$ 233.424 | R$ 404.711 | 7.2% | 4.2% | R$ 42 |
| Grupo 2 | 10.814 | R$ 6.423.096 | R$ 728.178 | R$ 370.659 | R$ 357.519 | 5.6% | 5.8% | R$ 33 |
| Grupo 3 | 11.410 | R$ 6.785.856 | R$ 767.887 | R$ 503.600 | R$ 264.287 | 3.9% | 7.4% | R$ 23 |

⚠️ = variante com problema de qualidade de dados; excluida da decisao.

## Leitura de negocio

- Faixa de cashback testada: de **4.2%** (Grupo 1) a **7.4%** (Grupo 3) sobre o GMV.
- Grupo 3 (mais cashback) gerou mais compradores (11.410 vs 9.633) e mais GMV, mas margem liquida de R$ 264.287 vs R$ 404.711.
- Aumentar cashback NAO se pagou em margem liquida neste teste.
- Significancia (t pareado por dia, vencedora vs vice): t=4.41, df=91, p=0.0000, n=92 dias.

> **Premissa-chave:** comparacao de margem total assume split de trafego igual entre variantes. Em caso de duvida, use margem/comprador e margem % GMV.

## Qualidade de dados e ressalvas

- Nenhum problema relevante detectado.

---
*Relatorio gerado automaticamente por `analisar_teste.py` em 2026-06-17.*