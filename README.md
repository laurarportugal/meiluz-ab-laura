# Analisador de Testes A/B de Cashback — Méliuz

Solução reutilizável que recebe o CSV de um teste A/B de cashback e devolve uma análise completa + decisão acionável: **"qual variante de cashback devemos escalar para 100% do tráfego?"**

A mesma solução roda nos 3 datasets sem alterar código — basta apontar o arquivo.

---

## Resultado dos 3 testes

| Parceiro | Variantes | Decisão | Margem líquida (vencedora) | Significância | Observação |
|---|---|---|---|---|---|
| A | 3 | Escalar Grupo 1 | R$ 404.711 | p < 0,0001 ✅ | Mais cashback gerou mais GMV, mas menos margem |
| B | 3 | Escalar Grupo 1 | R$ 286.570 | p < 0,0001 ✅ | Grupo 1 vence em volume e margem |
| C | 2 | INCONCLUSIVO (Grupo 1 provisório) | R$ 34.769 | — | Grupo 2 corrompido (cashback == comissão em 45/45 dias) |

**Insight central:** nos três parceiros, aumentar o % de cashback não se pagou em margem líquida. O cashback mais alto traz volume, mas o custo cresce mais rápido que a comissão.

**Por que margem líquida e não GMV?** GMV mede volume de vendas, não lucro. Escalar uma variante com GMV alto mas margem negativa destrói o resultado financeiro do Méliuz. A métrica correta é `comissão − cashback` — o que sobra de verdade após devolver o cashback ao usuário.

---

## Como rodar

**Requisitos:** Python 3. Zero dependências externas.

```bash
python analisar_teste.py data/dataset_01_parceiroA.csv
python analisar_teste.py data/dataset_02_parceiroB.csv
python analisar_teste.py data/dataset_03_parceiroC.csv
```

Opções disponíveis:
```bash
python analisar_teste.py data/dataset_01_parceiroA.csv \
    --nome "Cashback Parceiro A - Q1" \
    --descricao "Variação de % de cashback no Parceiro A"
```

**Saídas:**
- `relatorios/relatorio_<parceiro>.md` — relatório apresentável para gestor
- `planilha_acompanhamento.csv` — uma linha por teste rodado

---

## Via ferramenta de IA (Claude / Cursor / GPT / Gemini)

Use o arquivo `INSTRUCOES_IA.md` como prompt de sistema e peça em linguagem natural:

> "Analisa o teste em data/dataset_03_parceiroC.csv e me diz qual cashback escalar."

O agente roda o script, lê o relatório e explica a decisão.

---

## Arquitetura
**Decisões de projeto:**
- 1 script sem dependências → qualquer pessoa do time roda com um comando, em qualquer máquina, sem configurar ambiente
- Parametrizado pelo arquivo → mesmo código serve A, B, C e qualquer teste novo
- Robusto a dados ruins: encoding quebrado, moeda BR, cashback corrompido, datas desalinhadas
- A IA entra como camada de interpretação, não de execução — o script é a fonte da verdade

---

## Metodologia

- **Métrica principal:** margem líquida = comissão − cashback
- **Agregação por variante:** compradores, GMV, comissão, cashback, margem e métricas normalizadas
- **Checagens de qualidade:** cashback == comissão, margem negativa, amostra curta, outliers, coleta truncada
- **Significância estatística:** teste t pareado por dia (implementado sem numpy/scipy). p < 0,05 → recomendação firme; senão → INCONCLUSIVO