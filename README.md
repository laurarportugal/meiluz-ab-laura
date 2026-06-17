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

**Insight central:** nos três parceiros, aumentar o % de cashback não se pagou em margem líquida. O cashback mais alto traz volume, mas o custo cresce mais rápido que a comissão — a variante de menor cashback (Grupo 1) é a mais lucrativa nos três casos.

**Por que margem líquida e não GMV?** GMV mede volume de vendas, não lucro. Escalar uma variante com GMV alto mas margem negativa destrói o resultado financeiro do Méliuz. A métrica correta é `comissão − cashback` — o que sobra de verdade após devolver o cashback ao usuário.

---

## Como rodar

**Requisitos:** Python 3. Zero dependências externas — só a biblioteca padrão.

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

**Saídas geradas automaticamente:**
- `relatorios/relatorio_<parceiro>.md` — relatório apresentável para gestor
- `planilha_acompanhamento.csv` — uma linha por teste rodado (append)
- `dashboard.html` — dashboard visual com histórico de todos os testes

## Via ferramenta de IA (Claude / Cursor / GPT / Gemini)

Use o arquivo `INSTRUCOES_IA.md` como prompt de sistema e peça em linguagem natural:

> "Analisa o teste em data/dataset_03_parceiroC.csv e me diz qual cashback escalar."

O agente roda o script, lê o relatório gerado e explica a decisão em linguagem natural para o gestor.

---

## Arquitetura

```
meliuz-ab-laura/
├── analisar_teste.py          # script principal, parametrizado pelo CSV
├── INSTRUCOES_IA.md           # prompt para acionar via IA em linguagem natural
├── README.md
├── data/
│   ├── dataset_01_parceiroA.csv
│   ├── dataset_02_parceiroB.csv
│   └── dataset_03_parceiroC.csv
├── relatorios/
│   ├── relatorio_parceiro_a.md
│   ├── relatorio_parceiro_b.md
│   └── relatorio_parceiro_c.md
└── planilha_acompanhamento.csv
└── planilha_acompanhamento.csv
└── dashboard.html
```

**Decisões de projeto:**
- **1 script sem dependências** → qualquer pessoa do time roda com um comando, em qualquer máquina, sem configurar ambiente
- **Parametrizado pelo arquivo** → o mesmo código serve A, B, C e qualquer teste novo
- **Robusto a dados ruins** → trata encoding quebrado nos cabeçalhos, moeda BR com ponto de milhar, cashback corrompido, datas desalinhadas e linhas inválidas
- **IA como camada de interpretação** → o script é a fonte da verdade; o agente de IA entra para explicar a decisão em linguagem natural, não para executar lógica crítica

---

## Metodologia

- **Métrica principal:** margem líquida = comissão − cashback (lucro real do Méliuz)
- **Agregação por variante:** compradores, GMV, comissão, cashback, margem líquida e métricas normalizadas (margem % GMV, margem/comprador, cashback rate, take rate)
- **Checagens de qualidade de dados** com severidade (CRITICO / ATENCAO / INFO): cashback == comissão, margem negativa, amostra curta, janelas desalinhadas, coleta truncada, outliers de compradores
- **Significância estatística:** teste t pareado por dia entre a 1ª e a 2ª variante, implementado sem numpy/scipy. p < 0,05 → recomendação firme; caso contrário → INCONCLUSIVO

---

## Planilha de acompanhamento

Todos os testes analisados são registrados automaticamente:

[Acessar planilha no Google Sheets](https://docs.google.com/spreadsheets/d/19J5f9JT4ChXDiyb1Lq2yuSGgAS0ZhdRupl30AmRl1SA/edit?usp=sharing)