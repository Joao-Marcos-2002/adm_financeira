import numpy as np
import pandas as pd

from config import DIAS_UTEIS_ANO, N_CARTEIRAS

# Calculo de risco e retorno
def calcular_estatisticas(retornos, rf):
    """
    Calcula, para cada ativo, sendo a última coluna: o mercado:
      - Retorno médio anual         : média diária * 252
      - Risco (desvio-padrão) anual : desvio diário * raiz(252)
      - Coeficiente de variação     : risco / retorno (risco por unidade de retorno)
      - Beta                        : Cov(ativo, mercado) / Var(mercado)
      - Retorno exigido (CAPM)      : Rf + Beta * (Rm - Rf)
      - Índice de Sharpe            : (Retorno - Rf) / Risco
    """
    mercado = retornos.columns[-1]                    # última coluna = mercado
    ret_anual = retornos.mean() * DIAS_UTEIS_ANO      # retorno esperado anual
    risco_anual = retornos.std() * np.sqrt(DIAS_UTEIS_ANO)   # desvio-padrão anual

    # Beta: covariância com o mercado dividida pela variância do mercado
    var_mercado = retornos[mercado].var()
    betas = retornos.apply(lambda col: col.cov(retornos[mercado]) / var_mercado)

    rm = ret_anual[mercado]                           # retorno do mercado
    capm = rf + betas * (rm - rf)                     # retorno exigido pelo CAPM

    tabela = pd.DataFrame({
        "Retorno Esperado (a.a.)": ret_anual,
        "Risco - Desvio Padrão (a.a.)": risco_anual,
        # CV só faz sentido para retorno positivo; caso contrário fica vazio (NaN)
        "Coef. de Variação": risco_anual / ret_anual.where(ret_anual > 0),
        "Beta": betas,
        "Retorno CAPM (a.a.)": capm,
        "Índice de Sharpe": (ret_anual - rf) / risco_anual,
    })
    # Diferença entre retorno esperado e exigido (alfa de Jensen)
    tabela["Alfa de Jensen"] = tabela["Retorno Esperado (a.a.)"] - tabela["Retorno CAPM (a.a.)"]

    # Classificação do ativo segundo o beta
    def classificar(b):
        if b > 1.05:
            return "Agressivo (beta > 1)"
        if b < 0.95:
            return "Defensivo (beta < 1)"
        return "Neutro (beta ≈ 1)"
    tabela["Classificação"] = tabela["Beta"].apply(classificar)
    return tabela


def estatisticas_carteira(pesos, ret_medio, matriz_cov, rf):
    """
    Retorno da carteira  = soma(peso_i * retorno_i)
    Variância da carteira = pesos' * Matriz de Covariância * pesos
    Risco da carteira    = raiz da variância
    """
    retorno = float(np.dot(pesos, ret_medio))
    risco = float(np.sqrt(np.dot(pesos, np.dot(matriz_cov, pesos))))
    sharpe = (retorno - rf) / risco
    return retorno, risco, sharpe


def simular_carteiras(ret_medio, matriz_cov, rf, n=N_CARTEIRAS, semente=1):
    """
    Monte Carlo: gera n carteiras com pesos aleatórios (soma = 100%) para
    desenhar a fronteira eficiente e achar as carteiras notáveis.
    """
    rng = np.random.default_rng(semente)
    n_ativos = len(ret_medio)
    resultados = np.zeros((n, 3 + n_ativos))          # retorno, risco, sharpe, pesos...
    for i in range(n):
        w = rng.random(n_ativos)
        w = w / w.sum()                               # normaliza: soma dos pesos = 1
        r, s, sh = estatisticas_carteira(w, ret_medio, matriz_cov, rf)
        resultados[i, :3] = [r, s, sh]
        resultados[i, 3:] = w
    colunas = ["Retorno", "Risco", "Sharpe"] + list(ret_medio.index)
    return pd.DataFrame(resultados, columns=colunas)
