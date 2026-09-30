import os

import numpy as np
import matplotlib
matplotlib.use("Agg")                # gera gráficos em arquivo (sem abrir janela)
import matplotlib.pyplot as plt

# GRÁFICOS
def gerar_graficos(precos, tabela, carteiras, corr, rf, pasta, pesos_usuario, pt_usuario):
    """Gera e salva os gráficos PNG do relatório."""
    arquivos = []
    ativos = list(tabela.index[:-1])
    mercado = tabela.index[-1]

    # --- Gráfico 1: evolução do investimento de R$ 100 (retorno acumulado) ---
    plt.figure(figsize=(9, 5))
    # Normaliza a base em 100 pra comparar o crescimento relativo
    (precos / precos.iloc[0] * 100).plot(ax=plt.gca())
    plt.title("Evolução de R$ 100 investidos")
    plt.ylabel("Valor (R$)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    f = os.path.join(pasta, "grafico1_retorno_acumulado.png")
    # Salva em PNG e limpa a memória
    plt.savefig(f, dpi=120); plt.close(); arquivos.append(f)

    # --- Gráfico 2: Risco x Retorno de cada ativo ---
    plt.figure(figsize=(8, 5.5))
    # Plota ponto a ponto cada ativo e destaca o benchmark
    for nome in tabela.index:
        x = tabela.loc[nome, "Risco - Desvio Padrão (a.a.)"] * 100
        y = tabela.loc[nome, "Retorno Esperado (a.a.)"] * 100
        plt.scatter(x, y, s=90, marker="D" if nome == mercado else "o")
        plt.annotate(nome, (x, y), textcoords="offset points", xytext=(6, 6))
    plt.xlabel("Risco - desvio-padrão anual (%)")
    plt.ylabel("Retorno esperado anual (%)")
    plt.title("Risco x Retorno dos ativos")
    plt.grid(alpha=0.3); plt.tight_layout()
    f = os.path.join(pasta, "grafico2_risco_retorno.png")
    plt.savefig(f, dpi=120); plt.close(); arquivos.append(f)

    # --- Gráfico 3: Fronteira eficiente ---
    plt.figure(figsize=(9, 6))
    # Scatter colorido pelo Sharpe
    sc = plt.scatter(carteiras["Risco"] * 100, carteiras["Retorno"] * 100,
                     c=carteiras["Sharpe"], cmap="viridis", s=6, alpha=0.7)
    plt.colorbar(sc, label="Índice de Sharpe")
    # Pega as carteiras de destaque pra marcar no gráfico
    p_min = carteiras.loc[carteiras["Risco"].idxmin()]
    p_max = carteiras.loc[carteiras["Sharpe"].idxmax()]
    plt.scatter(p_min["Risco"] * 100, p_min["Retorno"] * 100, c="red",
                marker="*", s=250, label="Mínimo risco")
    plt.scatter(p_max["Risco"] * 100, p_max["Retorno"] * 100, c="gold",
                edgecolors="black", marker="*", s=250, label="Máximo Sharpe")
    # Posição da carteira que o usuário montou
    plt.scatter(pt_usuario[1] * 100, pt_usuario[0] * 100, c="white",
                edgecolors="black", marker="s", s=90, label="Sua carteira")
    plt.xlabel("Risco (%)"); plt.ylabel("Retorno (%)")
    plt.title("Fronteira Eficiente (simulação de carteiras)")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    f = os.path.join(pasta, "grafico3_fronteira_eficiente.png")
    plt.savefig(f, dpi=120); plt.close(); arquivos.append(f)

    # --- Gráfico 4: Mapa de correlação (base da diversificação) ---
    plt.figure(figsize=(7, 5.5))
    # Heatmap simples pra ver a correlação entre os papéis
    plt.imshow(corr.values, cmap="RdYlGn_r", vmin=-1, vmax=1)
    plt.colorbar(label="Correlação")
    plt.xticks(range(len(corr)), corr.columns, rotation=45, ha="right")
    plt.yticks(range(len(corr)), corr.index)
    # Escreve os valores numéricos dentro de cada quadrado
    for i in range(len(corr)):
        for j in range(len(corr)):
            plt.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center", fontsize=8)
    plt.title("Matriz de correlação dos retornos")
    plt.tight_layout()
    f = os.path.join(pasta, "grafico4_correlacao.png")
    plt.savefig(f, dpi=120); plt.close(); arquivos.append(f)

    # --- Gráfico 5: Linha do Mercado de Títulos (SML - CAPM) ---
    plt.figure(figsize=(8, 5.5))
    rm = tabela.loc[mercado, "Retorno Esperado (a.a.)"]
    # Cria o eixo x do beta ajustado pro limite dos dados
    bs = np.linspace(0, max(2.2, tabela["Beta"].max() + 0.2), 50)
    # Reta teórica do CAPM
    plt.plot(bs, (rf + bs * (rm - rf)) * 100, "k--", label="SML: Rf + β(Rm − Rf)")
    # Plota onde cada ativo caiu em relação à reta
    for nome in ativos:
        b = tabela.loc[nome, "Beta"]
        r = tabela.loc[nome, "Retorno Esperado (a.a.)"] * 100
        plt.scatter(b, r, s=80)
        plt.annotate(nome, (b, r), textcoords="offset points", xytext=(6, 6))
    plt.xlabel("Beta"); plt.ylabel("Retorno esperado anual (%)")
    plt.title("Linha do Mercado de Títulos (SML)\nAcima da linha = ativo com retorno acima do exigido")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    f = os.path.join(pasta, "grafico5_sml_capm.png")
    plt.savefig(f, dpi=120); plt.close(); arquivos.append(f)

    return arquivos