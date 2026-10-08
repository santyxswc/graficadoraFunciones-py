"""
@file analisis.py
@brief Búsqueda de extremos absolutos de una función en un intervalo cerrado.
@author Santiago Caicedo

Este módulo no sabe nada de gráficas: recibe una función y devuelve números.
Así se puede probar sin abrir ventanas y reutilizar en otros programas.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

import numpy as np

_RAZON_AUREA = (math.sqrt(5) - 1) / 2


class TipoExtremo(Enum):
    """Clase de punto destacado en la gráfica."""

    MAXIMO_ABSOLUTO = "Max. absoluto"
    MINIMO_ABSOLUTO = "Min. absoluto"
    EXTREMO_INTERVALO = "Extremo del intervalo"


@dataclass(frozen=True)
class Extremo:
    """Punto ``(x, y)`` de la función con su clasificación."""

    x: float
    y: float
    tipo: TipoExtremo

    def etiqueta(self, decimales: int = 3) -> str:
        """@return Texto para anotar el punto, por ejemplo ``Max. absoluto (3, 1)``."""
        return f"{self.tipo.value} ({_redondear(self.x, decimales)}, {_redondear(self.y, decimales)})"


@dataclass(frozen=True)
class AnalisisIntervalo:
    """Resultado de analizar una función en ``[desde, hasta]``."""

    desde: float
    hasta: float
    maximo: Extremo
    minimo: Extremo
    extremos_intervalo: tuple[Extremo, ...]

    @property
    def puntos(self) -> tuple[Extremo, ...]:
        """@return Máximo, mínimo y los extremos del intervalo que no coinciden con ellos."""
        destacados = [self.maximo, self.minimo]
        for extremo in self.extremos_intervalo:
            if all(not math.isclose(extremo.x, otro.x, abs_tol=1e-9) for otro in destacados):
                destacados.append(extremo)
        return tuple(destacados)


def analizar_extremos(
    funcion: Callable[[np.ndarray], np.ndarray],
    desde: float,
    hasta: float,
    muestras: int = 20_001,
) -> AnalisisIntervalo:
    """
    Encuentra el máximo y el mínimo absolutos de una función continua en un intervalo cerrado.

    Primero evalúa la función en una malla uniforme y luego refina cada
    candidato con búsqueda de sección áurea, lo que encuentra con precisión
    incluso picos sin derivada (como el de ``1 - |x-3|^(2/3)`` en ``x = 3``).

    @param funcion Función vectorizada de NumPy.
    @param desde Inicio del intervalo.
    @param hasta Fin del intervalo; mayor que ``desde``.
    @param muestras Puntos de la malla inicial (al menos 3).
    @return El análisis con el máximo, el mínimo y los valores en los bordes.
    @throws ValueError si el intervalo no es válido o la función no está definida en él.
    """
    if not (math.isfinite(desde) and math.isfinite(hasta)) or desde >= hasta:
        raise ValueError("El intervalo debe cumplir desde < hasta.")
    if muestras < 3:
        raise ValueError("Se necesitan al menos 3 muestras.")

    xs = np.linspace(desde, hasta, muestras)
    ys = np.asarray(funcion(xs), dtype=float)
    definidos = np.isfinite(ys)
    if not definidos.any():
        raise ValueError("La funcion no esta definida en ningun punto del intervalo.")

    paso = (hasta - desde) / (muestras - 1)
    x_max = _refinar(funcion, xs, ys, definidos, paso, desde, hasta, buscar_maximo=True)
    x_min = _refinar(funcion, xs, ys, definidos, paso, desde, hasta, buscar_maximo=False)

    bordes = tuple(
        Extremo(float(x), float(funcion(np.array([x]))[0]), TipoExtremo.EXTREMO_INTERVALO)
        for x in (desde, hasta)
        if math.isfinite(float(funcion(np.array([x]))[0]))
    )
    return AnalisisIntervalo(
        desde=desde,
        hasta=hasta,
        maximo=Extremo(x_max, _valor(funcion, x_max), TipoExtremo.MAXIMO_ABSOLUTO),
        minimo=Extremo(x_min, _valor(funcion, x_min), TipoExtremo.MINIMO_ABSOLUTO),
        extremos_intervalo=bordes,
    )


def _valor(funcion: Callable[[np.ndarray], np.ndarray], x: float) -> float:
    return float(funcion(np.array([x]))[0])


def _refinar(funcion, xs, ys, definidos, paso, desde, hasta, *, buscar_maximo: bool) -> float:
    """Toma el mejor punto de la malla y lo afina en el tramo vecino."""
    signo = 1.0 if buscar_maximo else -1.0
    puntaje = np.where(definidos, signo * ys, -np.inf)
    indice = int(np.argmax(puntaje))
    candidato = float(xs[indice])

    def objetivo(t: float) -> float:
        valor = _valor(funcion, t)
        return signo * valor if math.isfinite(valor) else -math.inf

    candidatos = [candidato]
    izquierda = max(desde, candidato - paso)
    derecha = min(hasta, candidato + paso)
    # Si un vecino está fuera del dominio (por ejemplo sqrt(x) cerca de 0), el extremo
    # suele estar justo en el borde del dominio: se ubica con bisección.
    for vecino in (izquierda, derecha):
        if vecino != candidato and not math.isfinite(_valor(funcion, vecino)):
            borde = _borde_del_dominio(funcion, definido=candidato, indefinido=vecino)
            candidatos.append(borde)
            if vecino == izquierda:
                izquierda = borde
            else:
                derecha = borde
    candidatos.append(_seccion_aurea(objetivo, izquierda, derecha))
    mejor = max(candidatos, key=objetivo)

    # Los extremos suelen caer en valores "redondos" (x = 3, no 2.9999999999997):
    # se prefiere el redondeo más simple que sea al menos igual de bueno.
    for decimales in range(10):
        redondeado = round(mejor, decimales)
        if desde <= redondeado <= hasta and objetivo(redondeado) >= objetivo(mejor):
            return float(redondeado)
    return mejor


def _borde_del_dominio(funcion, *, definido: float, indefinido: float) -> float:
    """Bisección entre un punto donde la función existe y otro donde no; devuelve el último definido."""
    for _ in range(100):
        medio = (definido + indefinido) / 2
        if medio in (definido, indefinido):
            break
        if math.isfinite(_valor(funcion, medio)):
            definido = medio
        else:
            indefinido = medio
    return definido


def _seccion_aurea(objetivo: Callable[[float], float], a: float, b: float, tolerancia: float = 1e-12) -> float:
    """Maximiza una función unimodal en ``[a, b]``."""
    c = b - _RAZON_AUREA * (b - a)
    d = a + _RAZON_AUREA * (b - a)
    fc, fd = objetivo(c), objetivo(d)
    for _ in range(200):
        if abs(b - a) <= tolerancia:
            break
        if fd > fc:
            a, c, fc = c, d, fd
            d = a + _RAZON_AUREA * (b - a)
            fd = objetivo(d)
        else:
            b, d, fd = d, c, fc
            c = b - _RAZON_AUREA * (b - a)
            fc = objetivo(c)
    return (a + b) / 2


def _redondear(valor: float, decimales: int) -> str:
    redondeado = round(valor, decimales)
    if redondeado == 0:
        redondeado = 0.0
    return f"{redondeado:g}"
