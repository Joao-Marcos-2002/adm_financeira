<!-- risco_retorno/
├── risco_retorno.py      # docstring, argparse e main() (continua sendo o ponto de entrada)
├── config.py             # constantes e valores padrão
├── coleta_dados.py       # coletar_yahoo, coletar_csv, gerar_simulado, capturar_dados
├── calculos.py           # calcular_estatisticas, estatisticas_carteira, simular_carteiras
├── carteira.py           # ler_pesos
├── graficos.py           # gerar_graficos
├── relatorios.py         # formatar_tabela, montar_interpretacao, gerar_relatorios
└── templates/
    └── relatorio.html    # modelo do relatório HTML -->




# Primeiramente, instale as dependências necessárias:
# pip install numpy pandas matplotlib yfinance


# Execute o programa:
# python risco_retorno.py


# Para abrir o relatorio HTML no navegador, execute o seguinte comando no terminal:
#    xdg-open relatorio_risco_retorno/relatorio.html