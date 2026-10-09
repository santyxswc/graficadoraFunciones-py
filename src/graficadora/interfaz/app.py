"""
@file app.py
@brief Punto de entrada de la aplicación de escritorio.
@author Santiago Caicedo

Se abre con ``graficadora-gui``, con ``graficadora`` sin argumentos o con
``python -m graficadora.interfaz.app``.
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QStyleFactory

from graficadora.interfaz.estilos import HOJA_DE_ESTILOS
from graficadora.interfaz.ventana import VentanaPrincipal


def crear_aplicacion() -> QApplication:
    """@return La aplicación de Qt con el estilo de la graficadora (reutiliza la que ya exista)."""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Graficadora")
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setStyleSheet(HOJA_DE_ESTILOS)
    return app


def main() -> int:
    """Abre la ventana y espera a que el usuario la cierre."""
    app = crear_aplicacion()
    ventana = VentanaPrincipal()
    ventana.show()
    return app.exec()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
