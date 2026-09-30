# -*- coding: utf-8 -*-
"""
Trabalho 1 - ADMINISTRAÇÃO FINANCEIRA (Sistemas de Informação)
TEma: Risco e retorno
ALunos: Isadora Horta e João Marcis Ribeiro Tolentino

OBJETIVO  Aplicar, na prática, os conceitos de Risco e Retorno vistos em sala:

  -  Retorno de um ativo 
  -Risco de um ativo (desvio-padrão e coeficiente de variação)
  - Covariância e correlação entre ativos (diversificação)
  - Retorno e risco de uma CARTEIRA (média ponderada e fórmula da variância)
  - Retorno exigido = Rf + Beta * (Rm - Rf)
  - Retorno por unidade de risco

CAPTURA DE DADOS (3 modos)
--------------------------
  - "yahoo"    : baixa preços reais da internet (biblioteca yfinance)
  - "csv"      : lê um arquivo CSV de preços (1ª coluna = data; demais = ativos)
  - "simulado" : gera preços de exemplo (garante que o programa sempre executa,
                 mesmo sem internet)

RELATÓRIOS GERADOS (pasta "relatorio_risco_retorno")

  - relatorio.txt   : relatório em texto com as análises
  - relatorio.html  : relatório visual com tabelas e gráficos
  - estatisticas.csv, correlacao.csv, precos.csv : dados calculados
  - graficos PNG    : retornos acumulados, risco x retorno, fronteira
                      eficiente, correlação e linha do mercado de títulos (SML)

                      
COMO EXECUTAR:
  Instalação das bibliotecas:
      pip install numpy pandas matplotlib yfinance

  Execução interativa (menu):
      python risco_retorno.py

  Execução direta (sem perguntas):
      python risco_retorno.py --modo simulado
      python risco_retorno.py --modo yahoo --ativos PETR4.SA VALE3.SA ITUB4.SA --mercado ^BVSP
      python risco_retorno.py --modo csv --arquivo meus_precos.csv --mercado IBOV

AUTORES: (preencher com os nomes da dupla)
==============================================================================
"""

import argparse                      # leitura de argumentos da linha de comando
import os                            # criação de pastas e caminhos
import sys                           # encerramento do programa em caso de erro

from config import DIAS_UTEIS_ANO, PASTA_SAIDA, TAXA_LIVRE_PADRAO
from coleta_dados import capturar_dados
from calculos import calcular_estatisticas, estatisticas_carteira, simular_carteiras
from carteira import ler_pesos
from graficos import gerar_graficos
from relatorios import gerar_relatorios


def main():
    # ---- Argumentos de linha de comando ----
    ap = argparse.ArgumentParser(description="Risco e Retorno - Adm. Financeira")
    ap.add_argument("--modo", choices=["yahoo", "csv", "simulado"])
    ap.add_argument("--ativos", nargs="+", help="tickers (modo yahoo)")
    ap.add_argument("--mercado", help="índice de mercado")
    ap.add_argument("--arquivo", help="caminho do CSV (modo csv)")
    ap.add_argument("--rf", type=float, default=TAXA_LIVRE_PADRAO,
                    help="taxa livre de risco em %% a.a.")
    ap.add_argument("--anos", type=int, default=3, help="anos de histórico (yahoo)")
    ap.add_argument("--pesos", nargs="+", help="pesos da carteira do usuário")
    args = ap.parse_args()

    print("=" * 60)
    print(" APLICAÇÃO DE RISCO E RETORNO - ADMINISTRAÇÃO FINANCEIRA")
    print("=" * 60)

    # 1) Captura dos dados de preços
    precos, modo = capturar_dados(args)
    if precos.shape[1] < 3:
        sys.exit("É necessário ao menos 2 ativos + 1 índice de mercado.")
    rf = args.rf / 100                                # converte % para decimal

    # 2) Retornos diários: variação percentual entre preços consecutivos
    retornos = precos.pct_change().dropna()

    # 3) Estatísticas de risco e retorno (ativos + mercado)
    tabela = calcular_estatisticas(retornos, rf)

    # 4) Matrizes de covariância (anualizada) e correlação (só ativos, sem mercado)
    ativos = list(retornos.columns[:-1])
    cov = retornos[ativos].cov() * DIAS_UTEIS_ANO
    corr = retornos.corr()                            # inclui o mercado
    ret_medio = tabela.loc[ativos, "Retorno Esperado (a.a.)"]

    # 5) Carteira do usuário
    pesos = ler_pesos(ativos, args)
    res_usuario = estatisticas_carteira(pesos, ret_medio.values, cov.values, rf)

    # 6) Fronteira por simulação
    carteiras = simular_carteiras(ret_medio, cov.values, rf)

    # 7) Saídas: pasta, gráficos e relatórios
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    graficos = gerar_graficos(precos, tabela, carteiras, corr, rf, PASTA_SAIDA,
                              pesos, res_usuario)
    relatorio = gerar_relatorios(precos, tabela, corr, carteiras, res_usuario,
                                 pesos, rf, modo, graficos, PASTA_SAIDA)

    # 8) Exibe o relatório
    print("\n" + relatorio)
    print(f"\nArquivos salvos em: {os.path.abspath(PASTA_SAIDA)}")
    print("Abra 'relatorio.html' no navegador para ver o relatório completo.")


if __name__ == "__main__":
    main()
