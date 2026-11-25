"""Erros e estruturas comuns aos métodos numéricos."""

from dataclasses import dataclass, field
from typing import Any


class ErroNumerico(ValueError):
    """Erro esperado por entrada inválida ou impossibilidade numérica."""


@dataclass
class ResultadoMetodo:
    """Resultado padronizado para exibição na interface."""

    resumo: str
    detalhes: list[str] = field(default_factory=list)
    colunas: list[str] = field(default_factory=list)
    iteracoes: list[list[Any]] = field(default_factory=list)
    convergiu: bool = True
    quantidade_iteracoes: int = 0
