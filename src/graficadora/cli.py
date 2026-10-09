"""
@file cli.py
@brief Interfaz de línea de comandos de la graficadora.
@author Santiago Caicedo

Sin argumentos abre la aplicación de escritorio (si está instalado PySide6).

Ejemplos::

    graficadora
    graficadora funcion "1 - abs(x-3)^(2/3)" --desde -5 --hasta 4
    graficadora relacion 2 3 5 6 10 26 --regla "2*x + 1" --guardar relacion.png
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from graficadora import __version__
from graficadora.analisis import analizar_extremos
from graficadora.expresion import FUNCIONES, Expresion, ExpresionInvalida
from graficadora.relaciones import RelacionBinaria


def crear_parser() -> argparse.ArgumentParser:
    """@return El analizador de argumentos con los subcomandos ``funcion`` y ``relacion``."""
    parser = argparse.ArgumentParser(
        prog="graficadora",
        description="Grafica funciones reales con sus extremos absolutos y relaciones binarias como digrafos.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="comando", required=True)

    funcion = sub.add_parser(
        "funcion",
        help="Grafica f(x) en un intervalo y marca su maximo y minimo absolutos.",
        description=f"Funciones disponibles: {', '.join(sorted(FUNCIONES))}. Constantes: pi, e. Potencia: ^ o **.",
    )
    funcion.add_argument("expresion", help='Expresion en x, por ejemplo "1 - abs(x-3)^(2/3)".')
    funcion.add_argument("--desde", type=float, default=-5.0, help="Inicio del intervalo (por defecto -5).")
    funcion.add_argument("--hasta", type=float, default=5.0, help="Fin del intervalo (por defecto 5).")
    funcion.add_argument("--guardar", metavar="ARCHIVO", help="Guarda la grafica (png, svg, pdf) en vez de mostrarla.")

    relacion = sub.add_parser("relacion", help="Dibuja la relacion y = regla(x) sobre un conjunto como un digrafo.")
    relacion.add_argument("conjunto", nargs="+", type=int, help="Elementos enteros del conjunto A.")
    relacion.add_argument("--regla", required=True, help='Regla en x, por ejemplo "2*x + 1".')
    relacion.add_argument("--guardar", metavar="ARCHIVO", help="Guarda la grafica (png, svg, pdf) en vez de mostrarla.")
    return parser


def main(argumentos: Sequence[str] | None = None) -> int:
    """
    Punto de entrada del comando ``graficadora``.

    @param argumentos Argumentos sin el nombre del programa; por defecto ``sys.argv[1:]``.
    @return Código de salida: 0 si todo salió bien, 2 si la entrada no es válida.
    """
    argumentos = sys.argv[1:] if argumentos is None else list(argumentos)
    if not argumentos:
        return _abrir_ventana()
    parser = crear_parser()
    args = parser.parse_args(argumentos)
    try:
        figura = _comando_funcion(args) if args.comando == "funcion" else _comando_relacion(args)
    except (ExpresionInvalida, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    _mostrar_o_guardar(figura, args.guardar)
    return 0


def _abrir_ventana() -> int:
    """Abre la aplicación de escritorio, o explica cómo instalarla si falta PySide6."""
    try:
        from graficadora.interfaz.app import main as abrir
    except ImportError:
        crear_parser().print_help()
        print('\nPara usar la ventana instale la interfaz: pip install "graficadora[gui]"', file=sys.stderr)
        return 2
    return abrir()


def _comando_funcion(args: argparse.Namespace):
    from graficadora.graficos import graficar_funcion

    funcion = Expresion(args.expresion)
    analisis = analizar_extremos(funcion, args.desde, args.hasta)
    for punto in analisis.puntos:
        print(punto.etiqueta())
    return graficar_funcion(funcion, funcion.texto, analisis, figura=_nueva_figura((9, 5.5)))


def _comando_relacion(args: argparse.Namespace):
    from graficadora.graficos import graficar_relacion

    regla = Expresion(args.regla)
    relacion = RelacionBinaria.desde_regla(args.conjunto, regla)
    pares = ", ".join(f"({x}, {y})" for x, y in sorted(relacion.pares)) or "ninguno"
    print(f"Pares: {pares}")
    for nombre, cumple in relacion.propiedades().items():
        print(f"{nombre.capitalize()}: {'si' if cumple else 'no'}")
    return graficar_relacion(relacion, regla.texto, figura=_nueva_figura((7, 6)))


def _nueva_figura(tamano: tuple[float, float]):
    """Figura administrada por pyplot, para poder mostrarla en una ventana con ``plt.show()``."""
    import matplotlib.pyplot as plt

    return plt.figure(figsize=tamano)


def _mostrar_o_guardar(figura, ruta: str | None) -> None:
    import matplotlib.pyplot as plt

    if ruta:
        figura.savefig(ruta, dpi=150)
        print(f"Grafica guardada en {ruta}")
    else:
        plt.show()
    plt.close(figura)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
