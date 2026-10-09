"""
@file __init__.py
@brief Graficadora de funciones reales y relaciones binarias.
@author Santiago Caicedo
"""

from graficadora.analisis import AnalisisIntervalo, Extremo, analizar_extremos
from graficadora.expresion import Expresion, ExpresionInvalida
from graficadora.relaciones import RelacionBinaria

__all__ = [
    "AnalisisIntervalo",
    "Expresion",
    "ExpresionInvalida",
    "Extremo",
    "RelacionBinaria",
    "analizar_extremos",
]

__version__ = "1.1.0"
