"""
@file test_expresion.py
@brief Pruebas del intérprete seguro de expresiones.
@author Santiago Caicedo
"""

import math
import warnings

import numpy as np
import pytest

from graficadora.expresion import Expresion, ExpresionInvalida


@pytest.mark.parametrize(
    ("texto", "x", "esperado"),
    [
        ("2*x + 1", 3, 7),
        ("x^2", -4, 16),
        ("x**2", -4, 16),
        ("1 - abs(x-3)^(2/3)", 3, 1),
        ("1 - abs(x-3)^(2/3)", -5, -3),
        ("sin(pi/2)", 0, 1),
        ("-x + e", 0, math.e),
        ("cbrt(x)", -8, -2),
    ],
)
def test_evalua_expresiones_validas(texto, x, esperado):
    assert float(Expresion(texto)(x)) == pytest.approx(esperado)


def test_evalua_arreglos_completos():
    resultado = Expresion("x * 2")(np.array([1.0, 2.0, 3.0]))
    assert resultado.tolist() == [2.0, 4.0, 6.0]


def test_una_constante_devuelve_un_valor_por_cada_x():
    assert Expresion("5")(np.zeros(4)).tolist() == [5.0] * 4


def test_fuera_del_dominio_devuelve_nan_sin_advertencias():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        valor = Expresion("sqrt(x)")(-1)
    assert math.isnan(float(valor))


@pytest.mark.parametrize(
    "texto",
    [
        "",
        "x +",
        "__import__('os').system('echo hola')",
        "y + 1",
        "x.real",
        "[x]",
        "sin(x, 2)",
        "'texto'",
        "x if x else 1",
        "True",
    ],
)
def test_rechaza_expresiones_invalidas_o_peligrosas(texto):
    with pytest.raises(ExpresionInvalida):
        Expresion(texto)
