"""
@file test_cli.py
@brief Pruebas de la línea de comandos (guardan imágenes en una carpeta temporal).
@author Santiago Caicedo
"""

from graficadora.cli import main


def test_funcion_guarda_la_grafica_e_imprime_los_extremos(tmp_path, capsys):
    destino = tmp_path / "funcion.png"
    codigo = main(["funcion", "1 - abs(x-3)^(2/3)", "--desde", "-5", "--hasta", "4", "--guardar", str(destino)])
    salida = capsys.readouterr().out
    assert codigo == 0
    assert destino.stat().st_size > 0
    assert "Max. absoluto (3, 1)" in salida
    assert "Min. absoluto (-5, -3)" in salida


def test_relacion_guarda_la_grafica_e_imprime_propiedades(tmp_path, capsys):
    destino = tmp_path / "relacion.svg"
    codigo = main(["relacion", "2", "3", "5", "6", "10", "26", "--regla", "2*x+1", "--guardar", str(destino)])
    salida = capsys.readouterr().out
    assert codigo == 0
    assert destino.exists()
    assert "Pares: (2, 5)" in salida
    assert "Transitiva: si" in salida


def test_expresion_invalida_devuelve_codigo_2(capsys):
    assert main(["funcion", "import os"]) == 2
    assert "Error" in capsys.readouterr().err
