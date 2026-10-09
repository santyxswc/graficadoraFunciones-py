"""
@file panel_relaciones.py
@brief Pantalla para dibujar una relación binaria y ver sus propiedades.
@author Santiago Caicedo
"""

from __future__ import annotations

import re

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from graficadora.expresion import Expresion, ExpresionInvalida
from graficadora.graficos import graficar_relacion
from graficadora.interfaz import estilos
from graficadora.relaciones import RelacionBinaria

EJEMPLOS = (
    ("y = 2x + 1", "2, 3, 5, 6, 10, 26", "2*x + 1"),
    ("Identidad: y = x", "1, 2, 3, 4, 5", "x"),
    ("Simétrica: y = 9 − x", "1, 2, 3, 4, 5, 6, 7, 8", "9 - x"),
    ("Siguiente: y = x + 1", "1, 2, 3, 4, 5, 6", "x + 1"),
    ("Mitad: y = x / 2", "1, 2, 4, 8, 16", "x / 2"),
)
"""(nombre, conjunto, regla) de cada ejemplo."""

NOMBRES_PROPIEDADES = {
    "reflexiva": "Reflexiva",
    "simetrica": "Simétrica",
    "antisimetrica": "Antisimétrica",
    "transitiva": "Transitiva",
}


def leer_conjunto(texto: str) -> list[int]:
    """
    Convierte lo que escribe el usuario en una lista de enteros.

    Acepta separadores de coma, punto y coma o espacios: ``"2, 3 5;6"``.

    @throws ValueError si algún elemento no es un número entero.
    """
    partes = [parte for parte in re.split(r"[,;\s]+", texto.strip()) if parte]
    try:
        return [int(parte) for parte in partes]
    except ValueError:
        raise ValueError(
            "El conjunto solo puede tener números enteros separados por comas, por ejemplo: 1, 2, 3."
        ) from None


class PanelRelaciones(QWidget):
    """Formulario con el conjunto y la regla a la izquierda, y el dígrafo a la derecha."""

    mensaje = Signal(str)
    """Texto corto para la barra de estado."""

    def __init__(self, padre: QWidget | None = None) -> None:
        super().__init__(padre)
        raiz = QHBoxLayout(self)
        raiz.setContentsMargins(32, 28, 32, 28)
        raiz.setSpacing(24)

        columna = QVBoxLayout()
        columna.setSpacing(12)
        columna.addWidget(estilos.titulo("Relaciones"))
        columna.addWidget(
            estilos.ayuda(
                "Escriba los elementos del conjunto A y la regla. Hay una flecha de x a y cuando "
                "y = regla(x) también está en A."
            )
        )

        self._ejemplos = QComboBox()
        self._ejemplos.addItem("Elegir un ejemplo…")
        for nombre, conjunto, _ in EJEMPLOS:
            self._ejemplos.addItem(f"{nombre}   A = {{{conjunto}}}")
        self._ejemplos.currentIndexChanged.connect(self._usar_ejemplo)
        columna.addWidget(self._ejemplos)

        columna.addWidget(estilos.etiqueta("Conjunto A"))
        self._conjunto = QLineEdit()
        self._conjunto.setPlaceholderText("1, 2, 3, 4")
        columna.addWidget(self._conjunto)
        columna.addWidget(estilos.etiqueta("Regla: y ="))
        self._regla = QLineEdit()
        self._regla.setObjectName("expresion")
        self._regla.setPlaceholderText("2*x + 1")
        columna.addWidget(self._regla)
        for campo in (self._conjunto, self._regla):
            campo.returnPressed.connect(self.dibujar)

        boton = estilos.boton_principal("Dibujar relación")
        boton.clicked.connect(self.dibujar)
        columna.addWidget(boton)

        self._error = QLabel()
        self._error.setObjectName("error")
        self._error.setWordWrap(True)
        self._error.hide()
        columna.addWidget(self._error)

        marco, self._resultados = estilos.tarjeta()
        columna.addWidget(marco)
        columna.addStretch()

        izquierda = QWidget()
        izquierda.setLayout(columna)
        izquierda.setFixedWidth(400)
        raiz.addWidget(izquierda)

        grafica, distribucion = estilos.tarjeta()
        self.figura = Figure(figsize=(7, 6))
        self.lienzo = FigureCanvasQTAgg(self.figura)
        distribucion.addWidget(self.lienzo, 1)
        raiz.addWidget(grafica, 1)

        self.relacion: RelacionBinaria | None = None
        self._ejemplos.setCurrentIndex(1)

    def _usar_ejemplo(self, indice: int) -> None:
        if indice <= 0:
            return
        _, conjunto, regla = EJEMPLOS[indice - 1]
        self.escribir(conjunto, regla)
        self.dibujar()

    def usar_ejemplo(self, indice: int) -> None:
        """Elige un ejemplo de la lista (1 = el primero) y lo dibuja."""
        self._ejemplos.setCurrentIndex(indice)

    def escribir(self, conjunto: str, regla: str) -> None:
        """Llena el formulario (lo usan los ejemplos y las pruebas)."""
        self._conjunto.setText(conjunto)
        self._regla.setText(regla)

    def dibujar(self) -> None:
        """Calcula la relación y la dibuja; los errores se explican debajo del botón."""
        try:
            regla = Expresion(self._regla.text())
            self.relacion = RelacionBinaria.desde_regla(leer_conjunto(self._conjunto.text()), regla)
        except (ExpresionInvalida, ValueError) as error:
            self.relacion = None
            self._error.setText(str(error))
            self._error.show()
            estilos.limpiar(self._resultados)
            return
        self._error.hide()
        graficar_relacion(self.relacion, regla.texto, figura=self.figura)
        self.lienzo.draw_idle()
        self._mostrar_resultados(self.relacion)
        self.mensaje.emit(f"Relación y = {regla.texto} dibujada con {len(self.relacion.pares)} par(es).")

    def _mostrar_resultados(self, relacion: RelacionBinaria) -> None:
        estilos.limpiar(self._resultados)
        seccion = QLabel("Propiedades")
        seccion.setObjectName("seccion")
        self._resultados.addWidget(seccion)
        for clave, cumple in relacion.propiedades().items():
            fila = QWidget()
            distribucion = QHBoxLayout(fila)
            distribucion.setContentsMargins(0, 0, 0, 0)
            distribucion.addWidget(QLabel(NOMBRES_PROPIEDADES[clave]))
            distribucion.addStretch()
            estado = QLabel("Sí" if cumple else "No")
            estado.setObjectName("si" if cumple else "no")
            distribucion.addWidget(estado)
            self._resultados.addWidget(fila)
        pares = ", ".join(f"({x},\u00a0{y})" for x, y in sorted(relacion.pares)) or "ninguno"
        titulo = QLabel("Pares de la relación")
        titulo.setObjectName("resultadoTitulo")
        lista = QLabel(pares)
        lista.setWordWrap(True)
        self._resultados.addWidget(titulo)
        self._resultados.addWidget(lista)
