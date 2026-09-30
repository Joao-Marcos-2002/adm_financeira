import numpy as np

# Lê os pesos da carteira. Se não informados, usa pesos iguais.
def ler_pesos(ativos, args):
    """
    Define os pesos da carteira do usuário. Se não informados, usa pesos iguais.
    Em modo interativo, pergunta os percentuais.
    """

    n = len(ativos)
    if args.pesos:
        # Se os pesos foram passados como argumento, usa diretamente
        w = np.array(args.pesos, dtype=float)
    elif args.modo is None:
        # Em modo interativo, pergunta os percentuais
        txt = input(f"Pesos (%) da sua carteira para {n} ativos, separados por espaço "
                    f"[iguais]: ").strip()
        w = np.array(txt.replace(",", ".").split(), dtype=float) if txt else np.ones(n)

    # Se não houver pesos informados, usa pesos iguais
    else:
        w = np.ones(n)
    if len(w) != n or w.sum() <= 0:
        print("Pesos inválidos. Usando pesos iguais.")
        w = np.ones(n)
    return w / w.sum()    # normaliza para somar 100%

