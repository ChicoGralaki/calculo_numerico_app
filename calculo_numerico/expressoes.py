"""Leitura segura de expressões matemáticas digitadas pelo usuário.

Não usa eval() nem executa código Python arbitrário. A expressão é analisada
com ast e somente operadores, constantes e funções matemáticas autorizadas
são aceitos.
"""

import ast
import math
import re
from collections.abc import Callable

from .erros import ErroNumerico

_FUNCOES: dict[str, Callable[..., float]] = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "abs": abs,
    "fabs": math.fabs,
    "floor": math.floor,
    "ceil": math.ceil,
}
_CONSTANTES = {"pi": math.pi, "e": math.e}
_OPERADORES_BINARIOS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a ** b,
    ast.Mod: lambda a, b: a % b,
}
_OPERADORES_UNARIOS = {
    ast.UAdd: lambda a: +a,
    ast.USub: lambda a: -a,
}


def _normalizar(expressao: str) -> str:
    texto = expressao.strip().replace("^", "**")
    # Apelidos usuais em português, sem alterar nomes maiores.
    texto = re.sub(r"\bsen\s*\(", "sin(", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\btg\s*\(", "tan(", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bln\s*\(", "log(", texto, flags=re.IGNORECASE)
    return texto


def _avaliar_no(no: ast.AST, x: float) -> float:
    if isinstance(no, ast.Expression):
        return _avaliar_no(no.body, x)
    if isinstance(no, ast.Constant) and isinstance(no.value, (int, float)):
        return float(no.value)
    if isinstance(no, ast.Name):
        nome = no.id.lower()
        if nome == "x":
            return float(x)
        if nome in _CONSTANTES:
            return _CONSTANTES[nome]
        raise ErroNumerico(f"Nome não permitido na expressão: '{no.id}'. Use apenas x, pi e e.")
    if isinstance(no, ast.BinOp) and type(no.op) in _OPERADORES_BINARIOS:
        esquerda = _avaliar_no(no.left, x)
        direita = _avaliar_no(no.right, x)
        if isinstance(no.op, ast.Pow) and abs(direita) > 1000:
            raise ErroNumerico("Expoente muito grande. Reduza o valor da potência.")
        resultado = _OPERADORES_BINARIOS[type(no.op)](esquerda, direita)
        return _validar_resultado(resultado)
    if isinstance(no, ast.UnaryOp) and type(no.op) in _OPERADORES_UNARIOS:
        return _validar_resultado(_OPERADORES_UNARIOS[type(no.op)](_avaliar_no(no.operand, x)))
    if isinstance(no, ast.Call) and isinstance(no.func, ast.Name):
        nome = no.func.id.lower()
        funcao = _FUNCOES.get(nome)
        if funcao is None:
            raise ErroNumerico(f"Função matemática não permitida: '{no.func.id}'.")
        if no.keywords:
            raise ErroNumerico("Não use argumentos nomeados nas funções matemáticas.")
        argumentos = [_avaliar_no(arg, x) for arg in no.args]
        try:
            return _validar_resultado(funcao(*argumentos))
        except TypeError as exc:
            raise ErroNumerico(f"Quantidade de argumentos inválida para {nome}().") from exc
    raise ErroNumerico(
        "Expressão inválida ou operação não permitida. Use x, números, +, -, *, /, ^ e funções como sin, cos, exp, ln e sqrt."
    )


def _validar_resultado(valor: float) -> float:
    if isinstance(valor, complex) or not math.isfinite(float(valor)):
        raise ErroNumerico("A expressão gerou um resultado não real ou não finito.")
    return float(valor)


def compilar_funcao(expressao: str) -> Callable[[float], float]:
    """Valida uma expressão e devolve uma função f(x)."""
    texto = _normalizar(expressao)
    if not texto:
        raise ErroNumerico("Informe a expressão da função f(x).")
    try:
        arvore = ast.parse(texto, mode="eval")
    except SyntaxError as exc:
        raise ErroNumerico("Não foi possível interpretar a expressão. Confira parênteses e operadores.") from exc

    def funcao(x: float) -> float:
        try:
            return _validar_resultado(_avaliar_no(arvore, float(x)))
        except ErroNumerico:
            raise
        except (ArithmeticError, ValueError, OverflowError) as exc:
            raise ErroNumerico(f"A função não pôde ser avaliada em x={x:g}: {exc}.") from exc

    # Verificação de que a árvore inteira contém somente nós conhecidos.
    # A avaliação em x=0 é deliberadamente evitada, pois a função pode não
    # estar definida nesse ponto (por exemplo, ln(x)).
    return funcao
