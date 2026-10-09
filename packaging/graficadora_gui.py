"""
@file graficadora_gui.py
@brief Punto de entrada que usa PyInstaller para crear el ejecutable de la ventana.
@author Santiago Caicedo
"""

import sys

from graficadora.interfaz.app import main

if __name__ == "__main__":
    sys.exit(main())
