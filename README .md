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

![Painel]("C:\Users\e_srms\Pictures\Screenshots\Captura de tela 2026-10-05 144552.png")

> Dupla: _(Lucas Mendes e Wendell Barboza)_
