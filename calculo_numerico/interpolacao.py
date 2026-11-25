"""Interpolação polinomial pelas formas de Lagrange e Newton."""

from .erros import ErroNumerico, ResultadoMetodo
from .validacao import validar_pontos


def _formatar_numero(valor: float) -> str:
    return f"{valor:.10g}"


def lagrange(xs: list[float], ys: list[float], x_alvo: float) -> ResultadoMetodo:
    """Calcula P_n(x) pela soma dos polinômios básicos de Lagrange."""
    validar_pontos(xs, ys)
    termos: list[float] = []
    linhas: list[list[object]] = []
    n = len(xs)
    for i in range(n):
        numerador = 1.0
        denominador = 1.0
        for j in range(n):
            if i != j:
                numerador *= x_alvo - xs[j]
                denominador *= xs[i] - xs[j]
        if denominador == 0:
            raise ErroNumerico("Os pontos de interpolação devem ter valores de x distintos.")
        li = numerador / denominador
        contribuicao = ys[i] * li
        termos.append(contribuicao)
        linhas.append([i, xs[i], ys[i], li, contribuicao])

    resultado = sum(termos)
    resumo = f"Interpolação de Lagrange em x* = {_formatar_numero(x_alvo)}:\nP(x*) = {_formatar_numero(resultado)}"
    resumo += f"\nGrau máximo do polinômio: {n - 1}."
    resumo += "\nO resultado é a soma de yᵢ·Lᵢ(x) para todos os pontos informados."
    return ResultadoMetodo(resumo, ["Os polinômios básicos Lᵢ(x) valem 1 no ponto xᵢ e 0 nos demais pontos da tabela."], ["i", "xᵢ", "yᵢ", "Lᵢ(x*)", "yᵢ·Lᵢ(x*)"], linhas, True, n)


def newton(xs: list[float], ys: list[float], x_alvo: float) -> ResultadoMetodo:
    """Calcula o interpolador de Newton por diferenças divididas."""
    validar_pontos(xs, ys)
    n = len(xs)
    tabela = [list(ys)]
    coluna = list(ys)
    coeficientes = [coluna[0]]

    for ordem in range(1, n):
        proxima = []
        for i in range(n - ordem):
            denominador = xs[i + ordem] - xs[i]
            if denominador == 0:
                raise ErroNumerico("Os pontos de interpolação devem ter valores de x distintos.")
            proxima.append((coluna[i + 1] - coluna[i]) / denominador)
        tabela.append(proxima)
        coeficientes.append(proxima[0])
        coluna = proxima

    # Forma encaixada (Horner generalizado) para avaliar o polinômio.
    valor = coeficientes[-1]
    for i in range(n - 2, -1, -1):
        valor = coeficientes[i] + (x_alvo - xs[i]) * valor

    termos = [f"{_formatar_numero(coeficientes[0])}"]
    produto = ""
    for ordem in range(1, n):
        produto += f"(x - {_formatar_numero(xs[ordem - 1])})"
        termos.append(f"({_formatar_numero(coeficientes[ordem])})·{produto}")
    polinomio = "P(x) = " + " + ".join(termos)

    linhas: list[list[object]] = []
    for i in range(n):
        linha: list[object] = [xs[i], tabela[0][i]]
        for ordem in range(1, n):
            linha.append(tabela[ordem][i] if i < len(tabela[ordem]) else "—")
        linhas.append(linha)

    resumo = f"Interpolação de Newton em x* = {_formatar_numero(x_alvo)}:\nP(x*) = {_formatar_numero(valor)}\n\nPolinômio na forma de Newton:\n{polinomio}"
    resumo += f"\nGrau máximo do polinômio: {n - 1}."
    return ResultadoMetodo(resumo, ["Os coeficientes são as primeiras entradas de cada coluna da tabela de diferenças divididas."], ["xᵢ", "f[xᵢ]", *[f"ordem {i}" for i in range(1, n)]], linhas, True, n - 1)
