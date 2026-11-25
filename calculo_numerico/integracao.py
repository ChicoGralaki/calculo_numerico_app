"""Integração numérica composta e integração de dados discretos."""

import math
from collections.abc import Callable

from .erros import ErroNumerico, ResultadoMetodo
from .validacao import validar_pontos


def _validar_subintervalos(n: int, minimo: int = 1) -> None:
    if not isinstance(n, int) or n < minimo:
        raise ErroNumerico(f"O número de subintervalos deve ser um inteiro maior ou igual a {minimo}.")
    if n > 5000:
        raise ErroNumerico("Para manter a interface responsiva, use no máximo 5.000 subintervalos.")


def trapezio_repetido(f: Callable[[float], float], a: float, b: float, n: int) -> ResultadoMetodo:
    """Regra composta dos trapézios com n subintervalos uniformes."""
    _validar_subintervalos(n, 1)
    if a == b:
        return ResultadoMetodo("Integral aproximada: 0 (limites iguais).", ["Não há intervalo de integração."], quantidade_iteracoes=0)
    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    ys = [f(x) for x in xs]
    soma_interiores = math.fsum(ys[1:-1])
    integral = (h / 2.0) * (ys[0] + 2.0 * soma_interiores + ys[-1])
    linhas = [[i, xs[i], ys[i], "extremo" if i in (0, n) else "peso 2"] for i in range(n + 1)]
    resumo = f"Integral aproximada (Trapézio Repetido): {integral:.12g}\nPasso h = {h:.12g}\nSubintervalos = {n}"
    return ResultadoMetodo(resumo, ["Fórmula: h/2 · [f(x₀) + 2·Σf(xᵢ) + f(xₙ)].", "Os pontos são igualmente espaçados no intervalo [a,b]."], ["i", "xᵢ", "f(xᵢ)", "participação"], linhas, True, n)


def simpson_repetida(f: Callable[[float], float], a: float, b: float, n: int) -> ResultadoMetodo:
    """Regra composta 1/3 de Simpson; n deve ser par."""
    _validar_subintervalos(n, 2)
    if n % 2 != 0:
        raise ErroNumerico("A Regra 1/3 de Simpson Repetida exige um número PAR de subintervalos.")
    if a == b:
        return ResultadoMetodo("Integral aproximada: 0 (limites iguais).", ["Não há intervalo de integração."], quantidade_iteracoes=0)
    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    ys = [f(x) for x in xs]
    soma_impares = math.fsum(ys[i] for i in range(1, n, 2))
    soma_pares = math.fsum(ys[i] for i in range(2, n, 2))
    integral = (h / 3.0) * (ys[0] + ys[-1] + 4.0 * soma_impares + 2.0 * soma_pares)
    linhas = []
    for i in range(n + 1):
        peso = 1 if i in (0, n) else (4 if i % 2 else 2)
        linhas.append([i, xs[i], ys[i], peso])
    resumo = f"Integral aproximada (Simpson 1/3 Repetida): {integral:.12g}\nPasso h = {h:.12g}\nSubintervalos = {n} (par)"
    return ResultadoMetodo(resumo, ["Fórmula: h/3 · [f(x₀) + f(xₙ) + 4·Σf(xᵢ ímpar) + 2·Σf(xᵢ par interno)].", "Os pontos são igualmente espaçados e o número de subintervalos deve ser par."], ["i", "xᵢ", "f(xᵢ)", "peso"], linhas, True, n)


def _validar_dados_discretos(xs: list[float], ys: list[float]) -> None:
    validar_pontos(xs, ys)
    if any(xs[i + 1] <= xs[i] for i in range(len(xs) - 1)):
        raise ErroNumerico("No caso discreto, os valores de x devem estar em ordem estritamente crescente.")


def trapezio_discreto(xs: list[float], ys: list[float]) -> ResultadoMetodo:
    """Integra dados tabelados pela soma das áreas de trapézios sucessivos.

    Aceita espaçamentos diferentes entre os pontos.
    """
    _validar_dados_discretos(xs, ys)
    parcelas = []
    linhas = []
    for i in range(len(xs) - 1):
        h = xs[i + 1] - xs[i]
        area = h * (ys[i] + ys[i + 1]) / 2.0
        parcelas.append(area)
        linhas.append([i + 1, f"[{xs[i]:.8g}, {xs[i + 1]:.8g}]", h, area])
    integral = math.fsum(parcelas)
    resumo = f"Integral aproximada dos dados discretos (Trapézios): {integral:.12g}\nQuantidade de pontos: {len(xs)}\nQuantidade de segmentos: {len(xs) - 1}"
    return ResultadoMetodo(resumo, ["Cada par de pontos consecutivos define um trapézio. O espaçamento pode ser não uniforme.", "Fórmula por segmento: (xᵢ₊₁-xᵢ)·[yᵢ+yᵢ₊₁]/2."], ["segmento", "intervalo", "Δx", "área"], linhas, True, len(xs) - 1)


def simpson_discreto(xs: list[float], ys: list[float], tolerancia_espacamento: float = 1e-8) -> ResultadoMetodo:
    """Simpson 1/3 em dados tabelados uniformes, com número par de segmentos."""
    _validar_dados_discretos(xs, ys)
    n = len(xs) - 1
    if n < 2 or n % 2 != 0:
        raise ErroNumerico("Simpson 1/3 em dados discretos exige pelo menos 3 pontos e quantidade PAR de segmentos.")
    passos = [xs[i + 1] - xs[i] for i in range(n)]
    h = math.fsum(passos) / n
    if max(abs(passo - h) for passo in passos) > tolerancia_espacamento * max(1.0, abs(h)):
        raise ErroNumerico("Simpson 1/3 exige pontos igualmente espaçados. Para espaçamento irregular, use Trapézios nos dados discretos.")
    soma_impares = math.fsum(ys[i] for i in range(1, n, 2))
    soma_pares = math.fsum(ys[i] for i in range(2, n, 2))
    integral = (h / 3.0) * (ys[0] + ys[-1] + 4.0 * soma_impares + 2.0 * soma_pares)
    linhas = []
    for i in range(len(xs)):
        peso = 1 if i in (0, n) else (4 if i % 2 else 2)
        linhas.append([i, xs[i], ys[i], peso])
    resumo = f"Integral aproximada dos dados discretos (Simpson 1/3): {integral:.12g}\nPasso h = {h:.12g}\nPontos = {len(xs)}; segmentos = {n}"
    return ResultadoMetodo(resumo, ["Os pontos devem ser igualmente espaçados e a quantidade de segmentos deve ser par.", "Fórmula: h/3 · [y₀ + yₙ + 4·Σyᵢ ímpar + 2·Σyᵢ par interno]."], ["i", "xᵢ", "yᵢ", "peso"], linhas, True, n)
