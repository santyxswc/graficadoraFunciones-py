"""
@file graficos.py
@brief Dibuja funciones y relaciones con Matplotlib.
@author Santiago Caicedo

Es la única parte del paquete que depende de Matplotlib y NetworkX. Recibe
resultados ya calculados (ver ``analisis`` y ``relaciones``) y solo se
encarga de dibujarlos.
"""

from __future__ import annotations

import math
from collections.abc import Callable

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.figure import Figure

from graficadora.analisis import AnalisisIntervalo, TipoExtremo
from graficadora.relaciones import RelacionBinaria

_COLORES = {
    TipoExtremo.MAXIMO_ABSOLUTO: "#2a9d8f",
    TipoExtremo.MINIMO_ABSOLUTO: "#e76f51",
    TipoExtremo.EXTREMO_INTERVALO: "#6c757d",
}


def graficar_funcion(
    funcion: Callable[[np.ndarray], np.ndarray],
    nombre: str,
    analisis: AnalisisIntervalo,
    muestras: int = 2_000,
) -> Figure:
    """
    Dibuja la función en el intervalo del análisis y marca sus extremos.

    @param funcion Función vectorizada de NumPy.
    @param nombre Texto de la función para el título y la leyenda.
    @param analisis Resultado de ``analizar_extremos``.
    @param muestras Puntos usados para trazar la curva.
    @return La figura de Matplotlib (sin mostrarla).
    """
    xs = np.linspace(analisis.desde, analisis.hasta, muestras)
    # Incluir los puntos destacados para que la curva pase exactamente por ellos (por ejemplo, un pico).
    xs = np.union1d(xs, [punto.x for punto in analisis.puntos])
    ys = funcion(xs)

    figura, ejes = plt.subplots(figsize=(9, 5.5), layout="constrained")
    ejes.plot(xs, ys, color="#264653", linewidth=2, label=f"f(x) = {nombre}")
    ejes.axhline(0, color="black", linewidth=0.6)
    ejes.axvline(0, color="black", linewidth=0.6)

    rango_y = float(np.nanmax(ys) - np.nanmin(ys)) or 1.0
    for punto in analisis.puntos:
        color = _COLORES[punto.tipo]
        ejes.scatter([punto.x], [punto.y], color=color, s=60, zorder=3)
        desplazamiento = 0.12 * rango_y if punto.tipo is not TipoExtremo.MINIMO_ABSOLUTO else -0.12 * rango_y
        ejes.annotate(
            punto.etiqueta(),
            xy=(punto.x, punto.y),
            xytext=(punto.x, punto.y + desplazamiento),
            ha="center",
            color=color,
            fontsize=10,
            arrowprops={"arrowstyle": "->", "color": color},
        )

    margen = 0.2 * rango_y
    ejes.set_ylim(float(np.nanmin(ys)) - margen, float(np.nanmax(ys)) + margen)
    ejes.set_title(f"f(x) = {nombre} en [{_numero(analisis.desde)}, {_numero(analisis.hasta)}]")
    ejes.set_xlabel("x")
    ejes.set_ylabel("f(x)")
    ejes.grid(True, alpha=0.3)
    ejes.legend(loc="best")
    return figura


def graficar_relacion(relacion: RelacionBinaria, regla: str) -> Figure:
    """
    Dibuja la relación como un dígrafo: un nodo por elemento y una flecha por par.

    @param relacion Relación ya calculada.
    @param regla Texto de la regla para el título.
    @return La figura de Matplotlib (sin mostrarla).
    """
    grafo = nx.DiGraph()
    grafo.add_nodes_from(relacion.conjunto)
    grafo.add_edges_from(relacion.pares)

    figura, ejes = plt.subplots(figsize=(7, 6), layout="constrained")
    posiciones = nx.circular_layout(grafo)
    nx.draw_networkx(
        grafo,
        posiciones,
        ax=ejes,
        node_color="#a8dadc",
        edgecolors="#1d3557",
        node_size=900,
        font_size=13,
        arrowsize=20,
        edge_color="#1d3557",
        width=1.6,
        connectionstyle="arc3,rad=0.1",
    )
    conjunto = ", ".join(str(x) for x in relacion.conjunto)
    pares = ", ".join(f"({x}, {y})" for x, y in sorted(relacion.pares)) or "ninguno"
    ejes.set_title(f"R = {{(x, y) en A x A : y = {regla}}}\nA = {{{conjunto}}}\nPares: {pares}")
    ejes.axis("off")
    return figura


def _numero(valor: float) -> str:
    return f"{valor:g}" if math.isfinite(valor) else str(valor)
