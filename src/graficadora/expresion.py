"""
@file expresion.py
@brief Interpreta expresiones matemáticas escritas como texto, de forma segura.
@author Santiago Caicedo

Usar ``eval`` con texto del usuario permite ejecutar cualquier código. Aquí la
expresión se analiza con el módulo ``ast`` y solo se aceptan números, la
variable ``x``, operadores aritméticos y una lista cerrada de funciones.
"""

from __future__ import annotations

import ast
import math
import operator
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np

_OPERADORES_BINARIOS: dict[type[ast.operator], Callable] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

_OPERADORES_UNARIOS: dict[type[ast.unaryop], Callable] = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

FUNCIONES: dict[str, Callable] = {
    "abs": np.abs,
    "sqrt": np.sqrt,
    "cbrt": np.cbrt,
    "exp": np.exp,
    "log": np.log,
    "ln": np.log,
    "log10": np.log10,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "asin": np.arcsin,
    "acos": np.arccos,
    "atan": np.arctan,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    "floor": np.floor,
    "ceil": np.ceil,
}
"""Funciones permitidas dentro de una expresión."""

CONSTANTES: dict[str, float] = {"pi": math.pi, "e": math.e}
"""Constantes permitidas dentro de una expresión."""

VARIABLE = "x"


class ExpresionInvalida(ValueError):
    """La expresión tiene sintaxis incorrecta o usa algo que no está permitido."""


@dataclass(frozen=True)
class Expresion:
    """
    Función real de una variable ``x`` definida por un texto.

    Acepta ``^`` como potencia. Se evalúa con NumPy, así que funciona tanto
    con un número como con un arreglo de valores.

    Ejemplo::

        >>> g = Expresion("1 - abs(x - 3)^(2/3)")
        >>> float(g(3))
        1.0
    """

    texto: str
    _arbol: ast.Expression = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        normalizado = self.texto.strip().replace("^", "**")
        if not normalizado:
            raise ExpresionInvalida("La expresion esta vacia.")
        try:
            arbol = ast.parse(normalizado, mode="eval")
        except SyntaxError as error:
            raise ExpresionInvalida(f"Sintaxis invalida en '{self.texto}'.") from error
        _validar(arbol.body)
        object.__setattr__(self, "_arbol", arbol)

    def __call__(self, x: float | np.ndarray) -> np.ndarray:
        """
        Evalúa la expresión.

        @param x Número o arreglo de valores de ``x``.
        @return Valores de la función. Donde no está definida (por ejemplo,
                raíz de un negativo) el resultado es ``nan``.
        """
        valores = np.asarray(x, dtype=float)
        with np.errstate(all="ignore"):
            resultado = _evaluar(self._arbol.body, valores)
        return np.broadcast_to(np.asarray(resultado, dtype=float), valores.shape).copy()

    def __str__(self) -> str:
        return self.texto


def _validar(nodo: ast.AST) -> None:
    """Recorre el árbol y rechaza cualquier construcción no permitida."""
    if isinstance(nodo, ast.Constant):
        if isinstance(nodo.value, bool) or not isinstance(nodo.value, (int, float)):
            raise ExpresionInvalida(f"Valor no permitido: {nodo.value!r}.")
    elif isinstance(nodo, ast.Name):
        if nodo.id != VARIABLE and nodo.id not in CONSTANTES:
            raise ExpresionInvalida(f"Nombre desconocido: '{nodo.id}'. Use la variable 'x'.")
    elif isinstance(nodo, ast.BinOp):
        if type(nodo.op) not in _OPERADORES_BINARIOS:
            raise ExpresionInvalida("Operador no permitido.")
        _validar(nodo.left)
        _validar(nodo.right)
    elif isinstance(nodo, ast.UnaryOp):
        if type(nodo.op) not in _OPERADORES_UNARIOS:
            raise ExpresionInvalida("Operador no permitido.")
        _validar(nodo.operand)
    elif isinstance(nodo, ast.Call):
        if not isinstance(nodo.func, ast.Name) or nodo.func.id not in FUNCIONES:
            permitidas = ", ".join(sorted(FUNCIONES))
            raise ExpresionInvalida(f"Funcion no permitida. Use una de: {permitidas}.")
        if nodo.keywords or len(nodo.args) != 1:
            raise ExpresionInvalida(f"La funcion '{nodo.func.id}' recibe exactamente un argumento.")
        _validar(nodo.args[0])
    else:
        raise ExpresionInvalida(f"Construccion no permitida: {type(nodo).__name__}.")


def _evaluar(nodo: ast.AST, x: np.ndarray):
    """Evalúa un árbol ya validado."""
    if isinstance(nodo, ast.Constant):
        return float(nodo.value)
    if isinstance(nodo, ast.Name):
        return x if nodo.id == VARIABLE else CONSTANTES[nodo.id]
    if isinstance(nodo, ast.BinOp):
        izquierda = _evaluar(nodo.left, x)
        derecha = _evaluar(nodo.right, x)
        return _OPERADORES_BINARIOS[type(nodo.op)](np.asarray(izquierda), np.asarray(derecha))
    if isinstance(nodo, ast.UnaryOp):
        return _OPERADORES_UNARIOS[type(nodo.op)](_evaluar(nodo.operand, x))
    if isinstance(nodo, ast.Call):
        return FUNCIONES[nodo.func.id](_evaluar(nodo.args[0], x))
    raise ExpresionInvalida("Expresion no validada.")  # pragma: no cover
