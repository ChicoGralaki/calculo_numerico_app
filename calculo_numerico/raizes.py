"""Métodos numéricos para determinação de raízes de funções reais."""

import math
from collections.abc import Callable

from .erros import ErroNumerico, ResultadoMetodo
from .validacao import validar_tolerancia


def _dados_comuns(tolerancia: float, max_iteracoes: int) -> None:
    validar_tolerancia(tolerancia)
    if not isinstance(max_iteracoes, int) or max_iteracoes < 1:
        raise ErroNumerico("O número máximo de iterações deve ser um inteiro positivo.")
    if max_iteracoes > 5000:
        raise ErroNumerico("Para evitar cálculos excessivamente longos, limite o máximo a 5.000 iterações.")


def bisseccao(
    f: Callable[[float], float], a: float, b: float,
    tolerancia: float = 1e-6, max_iteracoes: int = 100,
) -> ResultadoMetodo:
    """Bissecção com intervalo que mantém a mudança de sinal."""
    _dados_comuns(tolerancia, max_iteracoes)
    if not a < b:
        raise ErroNumerico("No método da Bissecção, o limite inferior a deve ser menor que b.")
    fa, fb = f(a), f(b)
    if fa == 0:
        return ResultadoMetodo(f"Raiz encontrada no extremo a: x = {a:.12g}.", [f"f(a) = {fa:.6g}"], quantidade_iteracoes=0)
    if fb == 0:
        return ResultadoMetodo(f"Raiz encontrada no extremo b: x = {b:.12g}.", [f"f(b) = {fb:.6g}"], quantidade_iteracoes=0)
    if (fa > 0 and fb > 0) or (fa < 0 and fb < 0):
        raise ErroNumerico("O intervalo informado não isola uma raiz: f(a) e f(b) têm o mesmo sinal.")

    linhas: list[list[object]] = []
    meio = (a + b) / 2.0
    fm = f(meio)
    for k in range(1, max_iteracoes + 1):
        meio = (a + b) / 2.0
        fm = f(meio)
        largura = b - a
        linhas.append([k, a, b, meio, fm, largura])
        if abs(fm) <= tolerancia or largura <= tolerancia:
            return ResultadoMetodo(
                f"Raiz aproximada: x = {meio:.12g}\nf(x) = {fm:.6g}\nIntervalo final = [{a:.12g}, {b:.12g}]",
                ["Critério: |f(x)| ≤ tolerância ou largura do intervalo ≤ tolerância."],
                ["k", "a", "b", "x médio", "f(x médio)", "b - a"], linhas, True, k,
            )
        if (fa < 0 < fm) or (fm < 0 < fa):
            b, fb = meio, fm
        else:
            a, fa = meio, fm

    return ResultadoMetodo(
        f"Última aproximação: x = {meio:.12g}\nf(x) = {fm:.6g}\nO método atingiu o limite de {max_iteracoes} iterações sem satisfazer a tolerância.",
        ["O intervalo continua contendo uma raiz, mas a precisão solicitada não foi atingida."],
        ["k", "a", "b", "x médio", "f(x médio)", "b - a"], linhas, False, max_iteracoes,
    )


def newton_raphson(
    f: Callable[[float], float], derivada: Callable[[float], float], x0: float,
    tolerancia: float = 1e-6, max_iteracoes: int = 100,
) -> ResultadoMetodo:
    """Newton-Raphson: x_(k+1) = x_k - f(x_k)/f'(x_k)."""
    _dados_comuns(tolerancia, max_iteracoes)
    fx = f(x0)
    if abs(fx) <= tolerancia:
        return ResultadoMetodo(f"A aproximação inicial já é uma raiz: x = {x0:.12g}.", [f"f(x0) = {fx:.6g}"], quantidade_iteracoes=0)

    linhas: list[list[object]] = []
    x = x0
    for k in range(1, max_iteracoes + 1):
        fx = f(x)
        dfx = derivada(x)
        if abs(dfx) <= 1e-14 * max(1.0, abs(fx)):
            raise ErroNumerico(f"A derivada é nula ou muito próxima de zero em x={x:.12g}. Newton não pode avançar.")
        proximo = x - fx / dfx
        f_proximo = f(proximo)
        passo = abs(proximo - x)
        linhas.append([k, x, fx, dfx, proximo, passo, f_proximo])
        if passo <= tolerancia and abs(f_proximo) <= tolerancia:
            return ResultadoMetodo(
                f"Raiz aproximada: x = {proximo:.12g}\nf(x) = {f_proximo:.6g}\n|x(k+1) - x(k)| = {passo:.6g}",
                ["Critério: variação entre aproximações e resíduo da função ≤ tolerância."],
                ["k", "x(k)", "f(x(k))", "f'(x(k))", "x(k+1)", "|Δx|", "f(x(k+1))"], linhas, True, k,
            )
        x = proximo

    return ResultadoMetodo(
        f"Última aproximação: x = {x:.12g}\nf(x) = {f(x):.6g}\nO método atingiu o limite de {max_iteracoes} iterações.",
        ["Newton pode divergir ou perder precisão dependendo da aproximação inicial."],
        ["k", "x(k)", "f(x(k))", "f'(x(k))", "x(k+1)", "|Δx|", "f(x(k+1))"], linhas, False, max_iteracoes,
    )


def secante(
    f: Callable[[float], float], x0: float, x1: float,
    tolerancia: float = 1e-6, max_iteracoes: int = 100,
) -> ResultadoMetodo:
    """Método da secante, que aproxima a derivada por diferenças finitas."""
    _dados_comuns(tolerancia, max_iteracoes)
    if x0 == x1:
        raise ErroNumerico("As duas aproximações iniciais da Secante devem ser diferentes.")
    f0, f1 = f(x0), f(x1)
    if abs(f0) <= tolerancia:
        return ResultadoMetodo(f"A primeira aproximação já é uma raiz: x = {x0:.12g}.", [f"f(x0) = {f0:.6g}"], quantidade_iteracoes=0)
    if abs(f1) <= tolerancia:
        return ResultadoMetodo(f"A segunda aproximação já é uma raiz: x = {x1:.12g}.", [f"f(x1) = {f1:.6g}"], quantidade_iteracoes=0)

    linhas: list[list[object]] = []
    for k in range(1, max_iteracoes + 1):
        denominador = f1 - f0
        escala = max(1.0, abs(f0), abs(f1))
        if abs(denominador) <= 1e-14 * escala:
            raise ErroNumerico("A diferença f(x1) - f(x0) ficou muito próxima de zero; a Secante não pode avançar.")
        x2 = x1 - f1 * (x1 - x0) / denominador
        f2 = f(x2)
        passo = abs(x2 - x1)
        linhas.append([k, x0, x1, x2, f2, passo])
        if passo <= tolerancia and abs(f2) <= tolerancia:
            return ResultadoMetodo(
                f"Raiz aproximada: x = {x2:.12g}\nf(x) = {f2:.6g}\n|x(k+1) - x(k)| = {passo:.6g}",
                ["Critério: variação entre aproximações e resíduo da função ≤ tolerância."],
                ["k", "x(k-1)", "x(k)", "x(k+1)", "f(x(k+1))", "|Δx|"], linhas, True, k,
            )
        x0, f0, x1, f1 = x1, f1, x2, f2

    return ResultadoMetodo(
        f"Última aproximação: x = {x1:.12g}\nf(x) = {f1:.6g}\nO método atingiu o limite de {max_iteracoes} iterações.",
        ["A Secante não mantém necessariamente um intervalo de isolamento; a convergência depende das aproximações iniciais."],
        ["k", "x(k-1)", "x(k)", "x(k+1)", "f(x(k+1))", "|Δx|"], linhas, False, max_iteracoes,
    )


def falsa_posicao(
    f: Callable[[float], float], a: float, b: float,
    tolerancia: float = 1e-6, max_iteracoes: int = 100,
) -> ResultadoMetodo:
    """Regula Falsi: secante limitada ao intervalo que contém a raiz."""
    _dados_comuns(tolerancia, max_iteracoes)
    if not a < b:
        raise ErroNumerico("Na Falsa Posição, o limite inferior a deve ser menor que b.")
    fa, fb = f(a), f(b)
    if fa == 0:
        return ResultadoMetodo(f"Raiz encontrada no extremo a: x = {a:.12g}.", [f"f(a) = {fa:.6g}"], quantidade_iteracoes=0)
    if fb == 0:
        return ResultadoMetodo(f"Raiz encontrada no extremo b: x = {b:.12g}.", [f"f(b) = {fb:.6g}"], quantidade_iteracoes=0)
    if (fa > 0 and fb > 0) or (fa < 0 and fb < 0):
        raise ErroNumerico("O intervalo informado não isola uma raiz: f(a) e f(b) têm o mesmo sinal.")

    linhas: list[list[object]] = []
    x = a
    fx = fa
    for k in range(1, max_iteracoes + 1):
        denominador = fb - fa
        if abs(denominador) <= 1e-15 * max(1.0, abs(fa), abs(fb)):
            raise ErroNumerico("Não foi possível calcular a interseção da secante com o eixo x (denominador nulo).")
        x = (a * fb - b * fa) / denominador
        fx = f(x)
        largura = b - a
        linhas.append([k, a, b, x, fx, largura])
        if abs(fx) <= tolerancia or largura <= tolerancia:
            return ResultadoMetodo(
                f"Raiz aproximada: x = {x:.12g}\nf(x) = {fx:.6g}\nIntervalo final = [{a:.12g}, {b:.12g}]",
                ["A cada iteração, o intervalo é atualizado para preservar a mudança de sinal."],
                ["k", "a", "b", "x (Regula Falsi)", "f(x)", "b - a"], linhas, True, k,
            )
        if (fa < 0 < fx) or (fx < 0 < fa):
            b, fb = x, fx
        else:
            a, fa = x, fx

    return ResultadoMetodo(
        f"Última aproximação: x = {x:.12g}\nf(x) = {fx:.6g}\nO método atingiu o limite de {max_iteracoes} iterações.",
        ["O método preserva o intervalo de isolamento, mas pode convergir lentamente se um extremo quase não mudar."],
        ["k", "a", "b", "x (Regula Falsi)", "f(x)", "b - a"], linhas, False, max_iteracoes,
    )
