# Vitto | Inteligência de Gestão

Sistema de análise das vendas registradas da Pizzaria do Vitto, com dashboard, previsão semanal de pedidos, agente de dados e biblioteca de Administração e Ciências Contábeis.

## Executar no computador

1. Abra um terminal nesta pasta.
2. Execute `python -m http.server 8000` com Python 3 instalado.
3. Abra http://localhost:8000 no navegador.

A interface lê arquivos JSON locais via HTTP. Para usar o chat e o tutor, abra em localhost ou HTTPS em um navegador com WebGPU. O primeiro uso baixa o modelo Qwen. A inferência ocorre no navegador.

## Conteúdo

- `index.html`, `style.css`, `app.js`: interface, indicadores, gráficos, filtros e exportação.
- `dados.json`: agregados históricos, métricas e previsão.
- `wiki.json`: 31 verbetes com exercícios e referências.
- `relatorio-vitto.pdf` e `relatorio-vitto.docx`: relatório estatístico.
- `apresentacao-vitto.pdf` e `apresentacao-vitto.pptx`: apresentação executiva em 8 slides.
- `previsao-vitto.csv`: estimativas e faixas semanais.
- `scripts/`: código para reproduzir os agregados e documentos.

## Dados e modelo

O histórico cobre 01/01/2025 a 03/08/2026. A projeção de quatro semanas usa média móvel de oito semanas, selecionada por validação cronológica, com teste separado nas 12 semanas finais. A previsão é retrospectiva em relação ao corte de 02/08/2026. O CSV original de transações não está publicado. Os agregados e documentos contêm valores comerciais; mantenha este repositório público somente se houver autorização para divulgar esses números.

Para reproduzir os resultados, instale as dependências listadas em `scripts/requirements.txt` e execute os scripts em sequência: `analyze.py`, `office.py`, `finalize.py` e `export_slides.py`.

A interface usa [Chart.js](https://www.chartjs.org/) e [WebLLM](https://github.com/mlc-ai/web-llm).
