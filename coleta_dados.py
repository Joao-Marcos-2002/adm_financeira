import os
import datetime

import numpy as np
import pandas as pd

from config import DIAS_UTEIS_ANO, ATIVOS_PADRAO, MERCADO_PADRAO, TAXA_LIVRE_PADRAO

# 3. CAPTURA DE DADOS

def coletar_yahoo(ativos, mercado, inicio, fim):
    """
    Baixa os preços de fechamento ajustados no Yahoo Finance.
    Retorna um DataFrame: linhas = datas, colunas = ativos + mercado.
    """
    try:
        import yfinance as yf        

    #em caso de biblioteca nao isntalada, exibe a mensagem abaixo ao usuario
    except ImportError:
        print("Biblioteca yfinance não instalada. Use: pip install yfinance")
        return None

    tickers = list(ativos) + [mercado]

    # Baixa os dados do Yahoo Finance
    print(f"Baixando dados de: {', '.join(tickers)} ...")
    dados = yf.download(tickers, start=inicio, end=fim,
                        auto_adjust=True, progress=False)

    #Verifica se os dados foram retornados
    if dados is None or len(dados) == 0:
        return None

    precos = dados["Close"]          # mantém o preço de fechamento
    precos = precos[tickers]         # para garantir a ordem das colunas
    precos = precos.dropna()         # remove datas com dados faltando
    return precos if len(precos) > 30 else None


def coletar_csv(caminho):
    """
    Lê um CSV de preços. Formato esperado:
        Data,ATIVO1,ATIVO2,...,MERCADO
        2023-01-02,25.3,70.1,...,110000
    A Ultima sera definida como índice de mercado.
    """
    if not os.path.exists(caminho):
        print(f"Arquivo não encontrado: {caminho}")
        return None
    precos = pd.read_csv(caminho, index_col=0, parse_dates=True)
    return precos.dropna()


def gerar_simulado(n_dias=750, semente=5):
    """
    Gera preços fictícios usando o modelo de índice único:
        retorno_ativo = alfa + beta * retorno_mercado + ruído
    Cada ativo tem um beta e um risco diferente
    """
    rng = np.random.default_rng(semente)          # gerador com uma semente fixa
    datas = pd.bdate_range(end=datetime.date.today(), periods=n_dias)

    # Retorno diário do mercado: usando média: 12% a.a. e volatilidade: 18% a.a.
    r_mercado = rng.normal(0.12 / DIAS_UTEIS_ANO,
                           0.18 / np.sqrt(DIAS_UTEIS_ANO), n_dias)

    # (beta, alfa, volatilidade específica anual) de cada ativo ficticio
    perfis = {
        "ACAO_DEFENSIVA": (0.60, 0.02, 0.10),
        "ACAO_NEUTRA":    (1.00, 0.01, 0.15),
        "ACAO_AGRESSIVA": (1.50, 0.00, 0.25),
        "ACAO_ESPECULATIVA": (1.90, -0.02, 0.40),
    }

    # Gera os retornos diários de cada ativo
    retornos = {}

    # Gera os retornos diários de cada ativo
    for nome, (beta, alfa, vol_esp) in perfis.items():
        ruido = rng.normal(0, vol_esp / np.sqrt(DIAS_UTEIS_ANO), n_dias)
        retornos[nome] = alfa / DIAS_UTEIS_ANO + beta * r_mercado + ruido
    retornos["MERCADO"] = r_mercado

    # Converte retornos em preços (base 100)
    precos = 100 * (1 + pd.DataFrame(retornos, index=datas)).cumprod()
    return precos

# Captura de dados de acordo com o modo escolhido (Yahoo, CSV ou Simulado)
def capturar_dados(args):
    """Decide o modo de captura, conforme argumentos ou menu interativo."""
    modo = args.modo

    # Menu interativo caso nenhum modo especifico for informado 
    if modo is None:
        print("\n=== CAPTURA DE DADOS ===")
        print("1 - Yahoo Finance (dados reais, exige internet)")
        print("2 - Arquivo CSV")
        print("3 - Dados simulados")
        escolha = input("Escolha (1/2/3) [3]: ").strip() or "3"
        modo = {"1": "yahoo", "2": "csv", "3": "simulado"}.get(escolha, "simulado")

        if modo == "yahoo":
            txt = input(f"Tickers separados por espaço [{' '.join(ATIVOS_PADRAO)}]: ").strip()
            args.ativos = txt.split() if txt else ATIVOS_PADRAO
            args.mercado = input(f"Índice de mercado [{MERCADO_PADRAO}]: ").strip() or MERCADO_PADRAO
        elif modo == "csv":
            args.arquivo = input("Caminho do CSV: ").strip()

        # Solicita a taxa livre de risco, com valor padrão caso o usuario não informe
        txt = input(f"Taxa livre de risco (% a.a.) [{TAXA_LIVRE_PADRAO}]: ").strip()
        args.rf = float(txt.replace(",", ".")) if txt else TAXA_LIVRE_PADRAO

    # Execucao da captura 
    precos = None
    if modo == "yahoo":
        fim = datetime.date.today()
        inicio = fim - datetime.timedelta(days=365 * args.anos)
        precos = coletar_yahoo(args.ativos or ATIVOS_PADRAO,
                               args.mercado or MERCADO_PADRAO, inicio, fim)
        
        #tratamento caso nao seja possivel obter os dados reais do yahoo finance
        if precos is None:
            print("Não foi possível obter dados reais. Usando dados simulados.")
            modo = "simulado"
    elif modo == "csv":
        precos = coletar_csv(args.arquivo)
        if precos is None:
            print("Falha ao ler o CSV. Usando dados simulados.")
            modo = "simulado"

    if precos is None:
        precos = gerar_simulado()

    #imprime informações sobre o modo de dados e o período
    print(f"Modo de dados: {modo.upper()} | {len(precos)} observações | "
          f"{precos.index[0].date()} a {precos.index[-1].date()}")
    return precos, modo

