"""
@file ventana.py
@brief Ventana principal con el menú lateral.
@author Santiago Caicedo
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from graficadora import __version__
from graficadora.interfaz.panel_funciones import PanelFunciones
from graficadora.interfaz.panel_relaciones import PanelRelaciones


class VentanaPrincipal(QMainWindow):
    """Menú a la izquierda y la pantalla elegida a la derecha."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Graficadora")
        self.resize(1300, 800)
        self.setMinimumSize(1050, 680)

        central = QWidget()
        fila = QHBoxLayout(central)
        fila.setContentsMargins(0, 0, 0, 0)
        fila.setSpacing(0)

        menu = QWidget()
        menu.setObjectName("menu")
        menu.setFixedWidth(220)
        self._menu = QVBoxLayout(menu)
        self._menu.setContentsMargins(0, 0, 0, 16)
        self._menu.setSpacing(0)
        marca = QLabel("Graficadora")
        marca.setObjectName("marca")
        submarca = QLabel("Funciones y relaciones")
        submarca.setObjectName("submarca")
        self._menu.addWidget(marca)
        self._menu.addWidget(submarca)
        self._menu.addStretch()
        version = QLabel(f"Versión {__version__}")
        version.setObjectName("submarca")
        self._menu.addWidget(version)

        self._pila = QStackedWidget()
        self._pila.setObjectName("contenido")
        self._opciones = QButtonGroup(self)
        self._opciones.idClicked.connect(self.mostrar)
        fila.addWidget(menu)
        fila.addWidget(self._pila, 1)
        self.setCentralWidget(central)

        self.funciones = PanelFunciones()
        self.relaciones = PanelRelaciones()
        for titulo, panel in (("Funciones", self.funciones), ("Relaciones", self.relaciones)):
            self._agregar(titulo, panel)
            panel.mensaje.connect(lambda texto: self.statusBar().showMessage(texto, 8000))
        self.mostrar(0)
        self.statusBar().showMessage("Elija un ejemplo o escriba su propia función.")

    def _agregar(self, titulo: str, panel: QWidget) -> None:
        indice = self._pila.addWidget(panel)
        boton = QPushButton(titulo)
        boton.setObjectName("opcionMenu")
        boton.setCheckable(True)
        self._opciones.addButton(boton, indice)
        self._menu.insertWidget(self._menu.count() - 2, boton)

    def mostrar(self, indice: int) -> None:
        """Muestra la pantalla en la posición indicada (0 = funciones, 1 = relaciones)."""
        self._opciones.button(indice).setChecked(True)
        self._pila.setCurrentIndex(indice)
