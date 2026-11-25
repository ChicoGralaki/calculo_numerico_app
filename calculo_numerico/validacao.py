"""Conversão e validação de entradas textuais da interface."""

import math
import re
from typing import Iterable

from .erros import ErroNumerico


def numero(texto: str, nome: str = "valor") -> float:
    """Converte texto para float; aceita vírgula como separador decimal."""
    bruto = str(texto).strip()
    if not bruto:
        raise ErroNumerico(f"Informe {nome}.")
    normalizado = bruto.replace(",", ".")
    try:
        valor = float(normalizado)
    except ValueError as exc:
        raise ErroNumerico(f"{nome.capitalize()} inválido: '{bruto}'.") from exc
    if not math.isfinite(valor):
        raise ErroNumerico(f"{nome.capitalize()} deve ser um número real finito.")
    return valor


def inteiro(texto: str, nome: str = "número de iterações", minimo: int = 1) -> int:
    bruto = str(texto).strip()
    if not bruto:
        raise ErroNumerico(f"Informe {nome}.")
    try:
        valor_float = float(bruto.replace(",", "."))
    except ValueError as exc:
        raise ErroNumerico(f"{nome.capitalize()} inválido: '{bruto}'.") from exc
    if not math.isfinite(valor_float) or not valor_float.is_integer():
        raise ErroNumerico(f"{nome.capitalize()} deve ser um número inteiro.")
    valor = int(valor_float)
    if valor < minimo:
        raise ErroNumerico(f"{nome.capitalize()} deve ser maior ou igual a {minimo}.")
    return valor


def lista_numeros(texto: str, nome: str) -> list[float]:
    """Lê valores separados por ponto e vírgula, espaços ou quebras de linha.

    O ponto e vírgula é o separador recomendado porque permite usar vírgula
    decimal, por exemplo: 0,5; 1,25; 2,0.
    """
    bruto = str(texto).strip()
    if not bruto:
        raise ErroNumerico(f"Informe os valores de {nome}.")
    partes = [p for p in re.split(r"[;\s]+", bruto) if p]
    valores = [numero(parte, f"{nome}, posição {i + 1}") for i, parte in enumerate(partes)]
    return valores


def matriz_numerica(texto: str, nome: str = "matriz A") -> list[list[float]]:
    """Lê matriz com uma linha por equação e valores separados por ; ou espaço.

    Também aceita vírgula decimal. Cada linha representa uma equação.
    """
    linhas = [linha.strip() for linha in str(texto).strip().splitlines() if linha.strip()]
    if not linhas:
        raise ErroNumerico(f"Informe a {nome}.")

    matriz: list[list[float]] = []
    for indice, linha in enumerate(linhas, start=1):
        valores = lista_numeros(linha, f"{nome}, linha {indice}")
        matriz.append(valores)

    quantidade_colunas = len(matriz[0])
    if any(len(linha) != quantidade_colunas for linha in matriz):
        raise ErroNumerico(f"Todas as linhas da {nome} devem ter a mesma quantidade de coeficientes.")
    return matriz


def validar_sistema(a: list[list[float]], b: Iterable[float]) -> tuple[list[list[float]], list[float]]:
    matriz = [linha[:] for linha in a]
    vetor = list(b)
    if not matriz or len(matriz) != len(matriz[0]):
        raise ErroNumerico("A matriz A deve ser quadrada (mesmo número de linhas e colunas).")
    if len(vetor) != len(matriz):
        raise ErroNumerico("O vetor b deve ter um elemento para cada linha da matriz A.")
    if any(not math.isfinite(v) for linha in matriz for v in linha) or any(not math.isfinite(v) for v in vetor):
        raise ErroNumerico("A matriz e o vetor devem conter apenas números finitos.")
    return matriz, vetor


def validar_tolerancia(tolerancia: float) -> None:
    if not math.isfinite(tolerancia) or tolerancia <= 0:
        raise ErroNumerico("A tolerância deve ser um número positivo e finito.")


def validar_pontos(xs: list[float], ys: list[float]) -> None:
    if len(xs) != len(ys):
        raise ErroNumerico("As listas de x e f(x) devem ter a mesma quantidade de valores.")
    if len(xs) < 2:
        raise ErroNumerico("Informe pelo menos dois pontos para interpolar ou integrar.")
    if len(set(xs)) != len(xs):
        raise ErroNumerico("Os valores de x devem ser distintos.")
    if any(not math.isfinite(v) for v in xs + ys):
        raise ErroNumerico("Os pontos devem conter apenas números finitos.")
