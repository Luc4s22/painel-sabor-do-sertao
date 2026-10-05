# Painel de Vendas: Sabor do Sertão

Painel interativo em Streamlit para analisar um ano de vendas da rede fictícia
Sabor do Sertão (Recife, Olinda, Caruaru, Petrolina e Garanhuns).

## Como rodar

```bash
pip install -r requirements.txt
python gerar_dados.py       
streamlit run app.py
```

O painel usa o CSV local automaticamente; também é possível enviar outro pela barra lateral.

## O que o painel tem

- **Exploração:** primeiras linhas, `describe()`, ausentes por coluna e tratamento de `avaliacao` (mediana, justificada na tela).
- **KPIs:** faturamento total, número de vendas, ticket médio e avaliação média.
- **Filtros:** cidade, categoria e período, aplicados a KPIs e gráficos.
- **Gráficos (abas):** faturamento mensal, por cidade, top 5 produtos, formas de pagamento e mapa de calor dia da semana x hora.
- **Insights e exportação:** três conclusões calculadas dos dados filtrados e botão para baixar o CSV filtrado.
- **Bônus:** aba "Explorador livre" para qualquer CSV (eixo X, eixo Y e tipo de gráfico).

## Print do painel

<img width="1905" height="888" alt="print_painel" src="https://github.com/user-attachments/assets/5b72d6fe-dcc1-4473-88de-0ce2bbf7f8c9" />


Dupla: Lucas Mendes e Wendell barboza
