"""
@file capturas.py
@brief Genera las capturas de pantalla del README.
@author Santiago Caicedo

Uso: ``QT_QPA_PLATFORM=offscreen python herramientas/capturas.py docs/imagenes``
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtTest import QTest

from graficadora.interfaz.app import crear_aplicacion
from graficadora.interfaz.ventana import VentanaPrincipal


def main(destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    app = crear_aplicacion()
    ventana = VentanaPrincipal()
    ventana.resize(1366, 820)
    ventana.show()

    ventana.funciones.usar_ejemplo(4)
    ventana.statusBar().clearMessage()
    QTest.qWait(300)
    ventana.grab().save(str(destino / "ventana-funciones.png"))

    ventana.mostrar(1)
    ventana.relaciones.usar_ejemplo(3)
    ventana.statusBar().clearMessage()
    QTest.qWait(300)
    ventana.grab().save(str(destino / "ventana-relaciones.png"))
    app.processEvents()


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "docs/imagenes"))
