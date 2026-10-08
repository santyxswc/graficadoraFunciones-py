"""
@file test_analisis.py
@brief Pruebas de la búsqueda de extremos absolutos.
@author Santiago Caicedo
"""

import pytest

from graficadora.analisis import TipoExtremo, analizar_extremos
from graficadora.expresion import Expresion


def test_funcion_original_del_curso():
    # g(x) = 1 - |x-3|^(2/3) en [-5, 4]: maximo en el pico x=3 y minimo en el borde x=-5.
    analisis = analizar_extremos(Expresion("1 - abs(x-3)^(2/3)"), -5, 4)
    assert analisis.maximo.x == 3
    assert analisis.maximo.y == 1
    assert analisis.minimo.x == pytest.approx(-5)
    assert analisis.minimo.y == pytest.approx(-3)
    assert analisis.maximo.etiqueta() == "Max. absoluto (3, 1)"


def test_extremos_interiores_de_una_parabola():
    analisis = analizar_extremos(Expresion("(x - 1.2345)^2"), -3, 3)
    assert analisis.minimo.x == pytest.approx(1.2345, abs=1e-6)
    assert analisis.maximo.x == pytest.approx(-3)


def test_puntos_no_repite_bordes_que_ya_son_extremos():
    analisis = analizar_extremos(Expresion("x"), 0, 1)
    tipos = [punto.tipo for punto in analisis.puntos]
    assert tipos == [TipoExtremo.MAXIMO_ABSOLUTO, TipoExtremo.MINIMO_ABSOLUTO]


def test_ignora_puntos_donde_la_funcion_no_esta_definida():
    analisis = analizar_extremos(Expresion("sqrt(x)"), -4, 9)
    assert analisis.maximo.y == pytest.approx(3)
    assert analisis.minimo.y == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize(("desde", "hasta"), [(2, 1), (1, 1), (float("nan"), 1)])
def test_rechaza_intervalos_invalidos(desde, hasta):
    with pytest.raises(ValueError):
        analizar_extremos(Expresion("x"), desde, hasta)


def test_rechaza_funciones_no_definidas_en_el_intervalo():
    with pytest.raises(ValueError):
        analizar_extremos(Expresion("log(x)"), -3, -1)
