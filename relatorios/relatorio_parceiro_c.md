# Relatorio de Teste A/B de Cashback — Parceiro C

- **Teste:** Cashback Parceiro C
- **Periodo:** 2011-07-01 a 2011-08-14 (45 dias)
- **Variantes:** 2
- **Metrica de decisao:** Margem liquida (comissao - cashback)
- **Gerado em:** 2026-06-17

## Recomendacao

> **[INCONCLUSIVO] Escalar Grupo 1 para 100% do trafego.**

Apenas 1 variante valida — sem comparativo A/B confiavel. Recomendacao provisoria.

## Comparativo entre variantes

| Variante | Compradores | GMV (vendas) | Comissao | Cashback | Margem liquida | Margem % GMV | Cashback % GMV | Margem/comprador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Grupo 1 | 4.549 | R$ 1.738.460 | R$ 121.693 | R$ 86.924 | R$ 34.769 | 2.0% | 5.0% | R$ 8 |
| Grupo 2 ⚠️ | 4.522 | R$ 1.685.235 | R$ 117.967 | R$ 117.967 | R$ 0 | 0.0% | 7.0% | R$ 0 |

⚠️ = variante com problema de qualidade de dados; excluida da decisao.

## Leitura de negocio

- Apenas o Grupo 1 e valido para analise.
  Margem liquida: R$ 34.769 | Margem % GMV: 2.0% | Margem/comprador: R$ 8.
- Acionar engenharia de dados para investigar as variantes excluidas antes de tomar decisao final.

> **Premissa-chave:** comparacao de margem total assume split de trafego igual entre variantes. Em caso de duvida, use margem/comprador e margem % GMV.

## Qualidade de dados e ressalvas

- [CRITICO] Grupo 2: cashback == comissao em 45/45 dias (margem zero). Suspeita de dado corrompido. Variante EXCLUIDA da decisao.
- [INFO] Teste com 2 variantes (A/B simples).

---
*Relatorio gerado automaticamente por `analisar_teste.py` em 2026-06-17.*