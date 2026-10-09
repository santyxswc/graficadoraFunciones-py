"""
@file panel_funciones.py
@brief Pantalla para graficar una función y ver sus extremos absolutos.
@author Santiago Caicedo
"""

from __future__ import annotations

from dataclasses import dataclass

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from graficadora.analisis import AnalisisIntervalo, TipoExtremo, analizar_extremos
from graficadora.expresion import Expresion, ExpresionInvalida
from graficadora.graficos import graficar_funcion
from graficadora.interfaz import estilos


@dataclass(frozen=True)
class Ejemplo:
    """Función de ejemplo que se puede elegir en la lista."""

    nombre: str
    expresion: str
    desde: float
    hasta: float


EJEMPLOS = (
    Ejemplo("Pico sin derivada", "1 - abs(x-3)^(2/3)", -5, 4),
    Ejemplo("Parábola", "x^2 - 4*x + 3", -1, 5),
    Ejemplo("Cúbica", "x^3 - 3*x", -2, 2),
    Ejemplo("Onda que se apaga", "sin(x) * exp(-x/4)", 0, 10),
    Ejemplo("Raíz cuadrada", "sqrt(x)", 0, 9),
)
"""Ejemplos para empezar sin escribir nada."""

TECLAS = (
    ("x²", "^2", 0),
    ("xⁿ", "^", 0),
    ("√x", "sqrt()", 1),
    ("|x|", "abs()", 1),
    ("sen", "sin()", 1),
    ("cos", "cos()", 1),
    ("tan", "tan()", 1),
    ("eˣ", "exp()", 1),
    ("ln", "ln()", 1),
    ("π", "pi", 0),
)
"""Botones de ayuda: (texto del botón, texto que se inserta, posiciones que retrocede el cursor)."""


class PanelFunciones(QWidget):
    """
    Formulario a la izquierda (función, intervalo y resultados) y gráfica a la derecha.

    No calcula nada por sí mismo: usa ``Expresion``, ``analizar_extremos`` y
    ``graficar_funcion``, igual que la línea de comandos.
    """

    mensaje = Signal(str)
    """Texto corto para la barra de estado."""

    def __init__(self, padre: QWidget | None = None) -> None:
        super().__init__(padre)
        raiz = QHBoxLayout(self)
        raiz.setContentsMargins(32, 28, 32, 28)
        raiz.setSpacing(24)

        columna = QVBoxLayout()
        columna.setSpacing(12)
        columna.addWidget(estilos.titulo("Funciones"))
        columna.addWidget(
            estilos.ayuda(
                "Escriba una función de x y el intervalo. El programa la dibuja y marca su "
                "máximo y su mínimo absolutos."
            )
        )

        self._ejemplos = QComboBox()
        self._ejemplos.addItem("Elegir un ejemplo…")
        for ejemplo in EJEMPLOS:
            self._ejemplos.addItem(f"{ejemplo.nombre}:  {ejemplo.expresion}")
        self._ejemplos.currentIndexChanged.connect(self._usar_ejemplo)
        columna.addWidget(self._ejemplos)

        columna.addWidget(estilos.etiqueta("f(x) ="))
        self._expresion = QLineEdit()
        self._expresion.setObjectName("expresion")
        self._expresion.setPlaceholderText("por ejemplo: x^2 - 4*x + 3")
        self._expresion.returnPressed.connect(self.graficar)
        columna.addWidget(self._expresion)

        teclado = QGridLayout()
        teclado.setSpacing(6)
        for indice, (texto, insertar, retroceso) in enumerate(TECLAS):
            tecla = QPushButton(texto)
            tecla.setObjectName("tecla")
            tecla.setToolTip(f"Escribe «{insertar}»")
            tecla.clicked.connect(lambda _=False, t=insertar, r=retroceso: self._insertar(t, r))
            teclado.addWidget(tecla, indice // 5, indice % 5)
        columna.addLayout(teclado)

        intervalo = QHBoxLayout()
        self._desde = self._campo_numero(-5)
        self._hasta = self._campo_numero(5)
        for texto, campo in (("Desde x =", self._desde), ("hasta x =", self._hasta)):
            intervalo.addWidget(estilos.etiqueta(texto))
            intervalo.addWidget(campo, 1)
        columna.addLayout(intervalo)

        boton = estilos.boton_principal("Graficar")
        boton.clicked.connect(self.graficar)
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
        self.figura = Figure(figsize=(8, 5.5))
        self.lienzo = FigureCanvasQTAgg(self.figura)
        # La barra de Matplotlib queda oculta: sus funciones se ofrecen con botones de texto claro.
        self._barra = NavigationToolbar2QT(self.lienzo, self)
        self._barra.hide()
        arriba = QHBoxLayout()
        self._acercar = QPushButton("Acercar")
        self._acercar.setToolTip("Dibuje un rectángulo sobre la gráfica para ampliar esa zona")
        self._mover = QPushButton("Mover")
        self._mover.setToolTip("Arrastre la gráfica para moverla")
        for boton, accion in ((self._acercar, self._barra.zoom), (self._mover, self._barra.pan)):
            boton.setCheckable(True)
            boton.clicked.connect(lambda _=False, a=accion: (a(), self._actualizar_modo()))
            arriba.addWidget(boton)
        original = QPushButton("Vista original")
        original.clicked.connect(self._barra.home)
        arriba.addWidget(original)
        arriba.addStretch()
        guardar = QPushButton("Guardar imagen…")
        guardar.clicked.connect(self._guardar_imagen)
        arriba.addWidget(guardar)
        distribucion.addLayout(arriba)
        distribucion.addWidget(self.lienzo, 1)
        raiz.addWidget(grafica, 1)

        self.analisis: AnalisisIntervalo | None = None
        self._ejemplos.setCurrentIndex(1)

    def _actualizar_modo(self) -> None:
        modo = str(self._barra.mode)
        self._acercar.setChecked(modo == "zoom rect")
        self._mover.setChecked(modo == "pan/zoom")

    def usar_ejemplo(self, indice: int) -> None:
        """Elige un ejemplo de la lista (1 = el primero) y lo grafica."""
        self._ejemplos.setCurrentIndex(indice)

    @staticmethod
    def _campo_numero(valor: float) -> QDoubleSpinBox:
        campo = QDoubleSpinBox()
        campo.setRange(-1_000_000, 1_000_000)
        campo.setDecimals(2)
        campo.setValue(valor)
        return campo

    def _usar_ejemplo(self, indice: int) -> None:
        if indice <= 0:
            return
        ejemplo = EJEMPLOS[indice - 1]
        self.escribir(ejemplo.expresion, ejemplo.desde, ejemplo.hasta)
        self.graficar()

    def escribir(self, expresion: str, desde: float, hasta: float) -> None:
        """Llena el formulario (lo usan los ejemplos y las pruebas)."""
        self._expresion.setText(expresion)
        self._desde.setValue(desde)
        self._hasta.setValue(hasta)

    def _insertar(self, texto: str, retroceso: int) -> None:
        self._expresion.insert(texto)
        self._expresion.cursorBackward(False, retroceso)
        self._expresion.setFocus()

    def graficar(self) -> None:
        """Interpreta la función, busca sus extremos y la dibuja; los errores se explican debajo del botón."""
        try:
            funcion = Expresion(self._expresion.text())
            self.analisis = analizar_extremos(funcion, self._desde.value(), self._hasta.value())
        except (ExpresionInvalida, ValueError) as error:
            self.analisis = None
            self._error.setText(str(error))
            self._error.show()
            estilos.limpiar(self._resultados)
            return
        self._error.hide()
        self._barra.update()  # la vista original pasa a ser la de esta gráfica
        graficar_funcion(funcion, funcion.texto, self.analisis, figura=self.figura)
        self.lienzo.draw_idle()
        self._mostrar_resultados(self.analisis)
        self.mensaje.emit(f"f(x) = {funcion.texto} graficada en [{self._desde.value():g}, {self._hasta.value():g}].")

    def _mostrar_resultados(self, analisis: AnalisisIntervalo) -> None:
        estilos.limpiar(self._resultados)
        seccion = QLabel("Resultados")
        seccion.setObjectName("seccion")
        self._resultados.addWidget(seccion)
        filas = [
            ("Máximo absoluto", analisis.maximo),
            ("Mínimo absoluto", analisis.minimo),
        ]
        filas += [("Extremo del intervalo", p) for p in analisis.puntos if p.tipo is TipoExtremo.EXTREMO_INTERVALO]
        for nombre, punto in filas:
            titulo = QLabel(nombre)
            titulo.setObjectName("resultadoTitulo")
            valor = QLabel(f"x = {_numero(punto.x)}    f(x) = {_numero(punto.y)}")
            valor.setObjectName("resultadoValor")
            self._resultados.addWidget(titulo)
            self._resultados.addWidget(valor)

    def _guardar_imagen(self) -> None:
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar gráfica", "grafica.png", "Imagen PNG (*.png);;Documento PDF (*.pdf);;SVG (*.svg)"
        )
        if ruta:
            self.figura.savefig(ruta, dpi=150)
            self.mensaje.emit(f"Gráfica guardada en {ruta}")


def _numero(valor: float) -> str:
    redondeado = round(valor, 4)
    return f"{0.0 if redondeado == 0 else redondeado:g}"
