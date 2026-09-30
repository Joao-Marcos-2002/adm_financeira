import os
import datetime
from string import Template

import pandas as pd

# 6. RELATÓRIOS (TXT e HTML)
def formatar_tabela(tabela):
    """Formata a tabela de estatísticas com % e casas decimais para exibição."""

    # Cria uma cópia para evitar alterar o DataFrame 
    t = tabela.copy()

    #Formata as colunas de retorno e risco como porcentagem com duas casas decimais
    for c in ["Retorno Esperado (a.a.)", "Risco - Desvio Padrão (a.a.)",
              "Retorno CAPM (a.a.)", "Alfa de Jensen"]:
        t[c] = (t[c] * 100).map("{:.2f}%".format)

    # Formata as colunas de coeficiente de variação, beta e índice com duas casas decimais
    for c in ["Coef. de Variação", "Beta", "Índice de Sharpe"]:
        t[c] = t[c].map(lambda v: "n/d" if pd.isna(v) else f"{v:.2f}")
    return t

# Monta a interpretação dos resultados
def montar_interpretacao(tabela, p_min, p_max, rf):
    """Cria o texto interpretativo (conclusões) a partir dos resultados."""

    # coloca os ativos (excluindo o mercado) e inicializa a lista de linhas
    ativos = tabela.iloc[:-1]
    linhas = []

    # Identifica os ativos destaques com base nas estatísticas
    maior_ret = ativos["Retorno Esperado (a.a.)"].idxmax()
    maior_risco = ativos["Risco - Desvio Padrão (a.a.)"].idxmax()
    menor_risco = ativos["Risco - Desvio Padrão (a.a.)"].idxmin()
    melhor_sharpe = ativos["Índice de Sharpe"].idxmax()



    # Tópicos sobre retorno, risco e índice
    linhas.append(f"- Maior retorno esperado: {maior_ret} "
                  f"({ativos.loc[maior_ret, 'Retorno Esperado (a.a.)']*100:.2f}% a.a.).")
    linhas.append(f"- Maior risco: {maior_risco}; menor risco: {menor_risco}. "
                  "Em geral, maior risco deve ser compensado por maior retorno esperado.")
    linhas.append(f"- Melhor relação retorno/risco (Sharpe): {melhor_sharpe} "
                  f"({ativos.loc[melhor_sharpe, 'Índice de Sharpe']:.2f}).")
    
    # Análise individual de cada ativo em relação ao CAPM e Beta
    for nome, linha in ativos.iterrows():
        situacao = "ACIMA" if linha["Alfa de Jensen"] > 0 else "ABAIXO"
        linhas.append(f"- {nome}: beta {linha['Beta']:.2f} ({linha['Classificação']}); "
                      f"retorno esperado {situacao} do exigido pelo CAPM.")
        
    # Conclusões sobre as carteiras ótimas da fronteira eficiente
    linhas.append(f"- Carteira de mínimo risco: risco {p_min['Risco']*100:.2f}% e retorno "
                  f"{p_min['Retorno']*100:.2f}%. Mostra o efeito da DIVERSIFICAÇÃO: o risco da "
                  "carteira tende a ser menor que a média ponderada dos riscos individuais.")
    linhas.append(f"- Carteira de máximo Sharpe: retorno {p_max['Retorno']*100:.2f}% e risco "
                  f"{p_max['Risco']*100:.2f}% (melhor retorno por unidade de risco).")
    linhas.append("- Observação: retornos passados não garantem retornos futuros; "
                  "o risco diversificável pode ser eliminado, o risco sistemático (beta) não.")
    return linhas


# Gera o relatório final (TXT e HTML) e salva os CSVs de apoio
def gerar_relatorios(precos, tabela, corr, carteiras, res_usuario, pesos, rf,
                     modo, graficos, pasta):
    """Gera relatório TXT e HTML e salva os CSVs de apoio."""
    
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    ativos = list(tabela.index[:-1])
    p_min = carteiras.loc[carteiras["Risco"].idxmin()]
    p_max = carteiras.loc[carteiras["Sharpe"].idxmax()]
    tab_fmt = formatar_tabela(tabela)
    interp = montar_interpretacao(tabela, p_min, p_max, rf)

    def texto_pesos(serie):
        return ", ".join(f"{a}: {serie[a]*100:.1f}%" for a in ativos)

    # Salva cada CSV 
    precos.to_csv(os.path.join(pasta, "precos.csv"), encoding="utf-8-sig")
    tabela.to_csv(os.path.join(pasta, "estatisticas.csv"), encoding="utf-8-sig")
    corr.to_csv(os.path.join(pasta, "correlacao.csv"), encoding="utf-8-sig")

    # Relatório 
    sep = "=" * 78
    txt = [
        sep, "RELATÓRIO DE RISCO E RETORNO", sep,
        f"Gerado em: {agora}",
        f"Origem dos dados: {modo.upper()}",
        f"Período: {precos.index[0].date()} a {precos.index[-1].date()} "
        f"({len(precos)} observações)",
        f"Taxa livre de risco (Rf): {rf*100:.2f}% a.a.",
        f"Ativos analisados: {', '.join(ativos)} | Mercado: {tabela.index[-1]}",
        "", sep, "1) ESTATÍSTICAS POR ATIVO", sep,
        tab_fmt.to_string(), "",
        sep, "2) MATRIZ DE CORRELAÇÃO", sep, corr.round(2).to_string(), "",
        sep, "3) CARTEIRA DEFINIDA PELO USUÁRIO", sep,
        f"Pesos: {texto_pesos(pd.Series(pesos, index=ativos))}",
        f"Retorno esperado: {res_usuario[0]*100:.2f}% a.a.",
        f"Risco (desvio-padrão): {res_usuario[1]*100:.2f}% a.a.",
        f"Índice de Sharpe: {res_usuario[2]:.2f}", "",
        sep, "4) CARTEIRAS NOTÁVEIS (fronteira eficiente)", sep,
        f"Mínimo risco  -> Retorno {p_min['Retorno']*100:.2f}% | Risco {p_min['Risco']*100:.2f}% "
        f"| Sharpe {p_min['Sharpe']:.2f}",
        f"   Pesos: {texto_pesos(p_min)}",
        f"Máximo Sharpe -> Retorno {p_max['Retorno']*100:.2f}% | Risco {p_max['Risco']*100:.2f}% "
        f"| Sharpe {p_max['Sharpe']:.2f}",
        f"   Pesos: {texto_pesos(p_max)}", "",
        sep, "5) INTERPRETAÇÃO DOS RESULTADOS", sep, *interp, "",
    ]
    with open(os.path.join(pasta, "relatorio.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(txt))

    # Relatório HTML para ser exibido 
    imgs = "".join(f'<img src="{os.path.basename(g)}" style="max-width:48%;margin:6px">'
                   for g in graficos)
    caminho_modelo = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "templates", "relatorio.html")
    with open(caminho_modelo, "r", encoding="utf-8") as fh:
        modelo = Template(fh.read())
    html = modelo.substitute(
        agora=agora,
        modo=modo.upper(),
        inicio=precos.index[0].date(),
        fim=precos.index[-1].date(),
        rf=f"{rf*100:.2f}",
        tabela_estatisticas=tab_fmt.to_html(border=0),
        tabela_correlacao=corr.round(2).to_html(border=0),
        pesos_usuario=texto_pesos(pd.Series(pesos, index=ativos)),
        ret_usuario=f"{res_usuario[0]*100:.2f}",
        risco_usuario=f"{res_usuario[1]*100:.2f}",
        sharpe_usuario=f"{res_usuario[2]:.2f}",
        pesos_min=texto_pesos(p_min),
        ret_min=f"{p_min['Retorno']*100:.2f}",
        risco_min=f"{p_min['Risco']*100:.2f}",
        pesos_max=texto_pesos(p_max),
        ret_max=f"{p_max['Retorno']*100:.2f}",
        risco_max=f"{p_max['Risco']*100:.2f}",
        interpretacao="".join(f"<li>{l[2:]}</li>" for l in interp),
        graficos=imgs,
    )
    with open(os.path.join(pasta, "relatorio.html"), "w", encoding="utf-8") as fh:
        fh.write(html)

    return "\n".join(txt)
