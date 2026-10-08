"""
@file test_relaciones.py
@brief Pruebas de las relaciones binarias.
@author Santiago Caicedo
"""

import pytest

from graficadora.expresion import Expresion
from graficadora.relaciones import RelacionBinaria


def test_relacion_original_del_curso():
    relacion = RelacionBinaria.desde_regla([2, 3, 5, 6, 10, 26], Expresion("2*x + 1"))
    assert relacion.pares == {(2, 5)}
    assert relacion.propiedades() == {
        "reflexiva": False,
        "simetrica": False,
        "antisimetrica": True,
        "transitiva": True,
    }


def test_identidad_es_reflexiva_simetrica_y_transitiva():
    relacion = RelacionBinaria.desde_regla([1, 2, 3], Expresion("x"))
    assert relacion.es_reflexiva()
    assert relacion.es_simetrica()
    assert relacion.es_transitiva()


def test_cadena_no_es_transitiva():
    relacion = RelacionBinaria.desde_regla([1, 2, 3], Expresion("x + 1"))
    assert relacion.pares == {(1, 2), (2, 3)}
    assert not relacion.es_transitiva()


def test_ignora_imagenes_no_enteras_y_repetidos():
    relacion = RelacionBinaria.desde_regla([1, 1, 2, 4], Expresion("x / 2"))
    assert relacion.conjunto == (1, 2, 4)
    assert relacion.pares == {(2, 1), (4, 2)}


def test_conjunto_vacio_es_invalido():
    with pytest.raises(ValueError):
        RelacionBinaria.desde_regla([], Expresion("x"))
