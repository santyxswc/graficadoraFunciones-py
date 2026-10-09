"""
@file test_interfaz.py
@brief Pruebas de la aplicación de escritorio con clics y teclas simulados (pytest-qt).
@author Santiago Caicedo
"""

import pytest

pytest.importorskip("PySide6")
pytest.importorskip("pytestqt")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton  # noqa: E402

from graficadora.interfaz.panel_relaciones import leer_conjunto  # noqa: E402
from graficadora.interfaz.ventana import VentanaPrincipal  # noqa: E402


@pytest.fixture
def ventana(qtbot):
    ventana = VentanaPrincipal()
    qtbot.addWidget(ventana)
    ventana.show()
    return ventana


def _boton(panel, texto):
    return next(b for b in panel.findChildren(QPushButton) if b.text() == texto)


def _error_visible(panel):
    etiqueta = panel.findChild(QLabel, "error")
    return not etiqueta.isHidden(), etiqueta.text()


def test_abre_con_un_ejemplo_ya_graficado(ventana):
    analisis = ventana.funciones.analisis
    assert analisis is not None
    assert (analisis.maximo.x, analisis.maximo.y) == (3, 1)
    assert ventana.relaciones.relacion.pares == {(2, 5)}


def test_escribir_con_el_teclado_de_ayuda_y_graficar(ventana, qtbot):
    panel = ventana.funciones
    campo = panel.findChild(QLineEdit, "expresion")
    campo.clear()
    qtbot.mouseClick(_boton(panel, "√x"), Qt.LeftButton)
    qtbot.keyClicks(campo, "x")
    assert campo.text() == "sqrt(x)"
    panel.escribir(campo.text(), 0, 16)
    qtbot.mouseClick(_boton(panel, "Graficar"), Qt.LeftButton)
    assert panel.analisis.maximo.y == pytest.approx(4)
    assert not _error_visible(panel)[0]


def test_una_funcion_invalida_se_explica_sin_cerrar_la_ventana(ventana, qtbot):
    panel = ventana.funciones
    panel.escribir("2x + 1", -1, 1)
    qtbot.mouseClick(_boton(panel, "Graficar"), Qt.LeftButton)
    visible, texto = _error_visible(panel)
    assert visible
    assert "2*x" in texto
    assert panel.analisis is None


def test_intervalo_al_reves_se_explica(ventana, qtbot):
    panel = ventana.funciones
    panel.escribir("x", 5, 1)
    qtbot.mouseClick(_boton(panel, "Graficar"), Qt.LeftButton)
    assert _error_visible(panel)[0]


def test_dibujar_una_relacion_y_ver_sus_propiedades(ventana, qtbot):
    ventana.mostrar(1)
    panel = ventana.relaciones
    panel.escribir("1 2 3", "x")
    qtbot.mouseClick(_boton(panel, "Dibujar relación"), Qt.LeftButton)
    assert panel.relacion.propiedades() == {
        "reflexiva": True,
        "simetrica": True,
        "antisimetrica": True,
        "transitiva": True,
    }
    estados = [e.text() for e in panel.findChildren(QLabel) if e.objectName() in ("si", "no")]
    assert estados == ["Sí", "Sí", "Sí", "Sí"]


def test_conjunto_invalido_se_explica(ventana, qtbot):
    panel = ventana.relaciones
    panel.escribir("1, dos, 3", "x")
    qtbot.mouseClick(_boton(panel, "Dibujar relación"), Qt.LeftButton)
    visible, texto = _error_visible(panel)
    assert visible
    assert "enteros" in texto


@pytest.mark.parametrize(("texto", "esperado"), [("1, 2, 3", [1, 2, 3]), ("4 5;6", [4, 5, 6]), (" -1 ,0 ", [-1, 0])])
def test_leer_conjunto_acepta_varios_separadores(texto, esperado):
    assert leer_conjunto(texto) == esperado


def test_sin_argumentos_la_linea_de_comandos_abre_la_ventana(monkeypatch):
    import graficadora.interfaz.app as app
    from graficadora.cli import main

    llamadas = []
    monkeypatch.setattr(app, "main", lambda: llamadas.append(True) or 0)
    assert main([]) == 0
    assert llamadas == [True]
