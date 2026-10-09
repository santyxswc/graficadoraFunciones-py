"""
@file estilos.py
@brief Hoja de estilos y piezas visuales comunes de la ventana.
@author Santiago Caicedo
"""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

VERDE = "#1f6f5c"
VERDE_OSCURO = "#17453b"
ROJO = "#b42318"

HOJA_DE_ESTILOS = """
* { font-size: 11pt; }
QMainWindow, QWidget#contenido { background: #f4f5f2; }
QWidget#menu { background: #17453b; }
QLabel#marca { color: white; font-size: 15pt; font-weight: 700; padding: 22px 18px 4px 18px; }
QLabel#submarca { color: #a7c7bd; font-size: 9.5pt; padding: 0 18px 18px 18px; }
QPushButton#opcionMenu {
    color: #e4f0ec; background: transparent; border: none; text-align: left;
    padding: 12px 18px; margin: 2px 10px; border-radius: 8px; font-size: 11.5pt;
}
QPushButton#opcionMenu:hover { background: #1f5a4d; }
QPushButton#opcionMenu:checked { background: white; color: #17453b; font-weight: 600; }
QLabel#titulo { font-size: 20pt; font-weight: 700; color: #1d2a26; }
QLabel#ayuda { color: #66706c; font-size: 10.5pt; }
QLabel#seccion { font-size: 12pt; font-weight: 600; color: #1d2a26; }
QLabel#etiqueta { color: #4b5753; font-size: 10pt; font-weight: 600; }
QLabel#error {
    color: #b42318; background: #fdf0ef; border: 1px solid #f0c4c0; border-radius: 8px; padding: 8px 10px;
}
QFrame#tarjeta { background: white; border: 1px solid #dfe3df; border-radius: 12px; }
QLabel#resultadoTitulo { color: #66706c; font-size: 10pt; }
QLabel#resultadoValor { color: #1d2a26; font-size: 15pt; font-weight: 700; }
QLabel#si { color: #1f6f5c; background: #e3f2ec; border-radius: 10px; padding: 4px 10px; font-weight: 600; }
QLabel#no { color: #8a3b12; background: #fbeee6; border-radius: 10px; padding: 4px 10px; font-weight: 600; }
QPushButton {
    background: white; border: 1px solid #cdd3cf; border-radius: 8px; padding: 8px 14px; color: #1d2a26;
}
QPushButton:hover { background: #eef2ef; }
QPushButton#tecla { padding: 6px 0; min-width: 52px; font-family: "DejaVu Sans", "Segoe UI", sans-serif; }
QPushButton#principal {
    background: #1f6f5c; border: 1px solid #1f6f5c; color: white; font-weight: 600; padding: 11px 20px;
}
QPushButton#principal:hover { background: #195c4c; }
QLineEdit, QComboBox, QDoubleSpinBox {
    background: white; border: 1px solid #cdd3cf; border-radius: 8px; padding: 7px 10px; min-height: 22px;
}
QLineEdit#expresion { font-size: 14pt; font-family: "DejaVu Sans Mono", "Consolas", monospace; }
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus { border: 2px solid #1f6f5c; padding: 6px 9px; }
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button { width: 0; border: none; }
QStatusBar { background: white; color: #4b5753; border-top: 1px solid #dfe3df; }
QToolBar { background: transparent; border: none; spacing: 4px; }
"""
"""Mismos colores y forma que la aplicación de escritorio del almacén."""


def titulo(texto: str) -> QLabel:
    """@return Etiqueta con el título grande de una pantalla."""
    etiqueta = QLabel(texto)
    etiqueta.setObjectName("titulo")
    return etiqueta


def ayuda(texto: str) -> QLabel:
    """@return Texto gris de ayuda que se ajusta al ancho."""
    etiqueta = QLabel(texto)
    etiqueta.setObjectName("ayuda")
    etiqueta.setWordWrap(True)
    return etiqueta


def etiqueta(texto: str) -> QLabel:
    """@return Rótulo pequeño para un campo de un formulario."""
    rotulo = QLabel(texto)
    rotulo.setObjectName("etiqueta")
    return rotulo


def boton_principal(texto: str) -> QPushButton:
    """@return Botón verde para la acción principal de la pantalla."""
    boton = QPushButton(texto)
    boton.setObjectName("principal")
    return boton


def tarjeta() -> tuple[QFrame, QVBoxLayout]:
    """@return Un recuadro blanco con bordes redondeados y su distribución vertical."""
    marco = QFrame()
    marco.setObjectName("tarjeta")
    distribucion = QVBoxLayout(marco)
    distribucion.setContentsMargins(18, 16, 18, 16)
    distribucion.setSpacing(10)
    return marco, distribucion


def limpiar(distribucion) -> None:
    """Quita y destruye todos los widgets de una distribución."""
    while distribucion.count():
        elemento = distribucion.takeAt(0)
        widget: QWidget | None = elemento.widget()
        if widget is not None:
            widget.setParent(None)  # se suelta ya, aunque Qt lo destruya un poco después
            widget.deleteLater()
