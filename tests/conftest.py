"""
@file conftest.py
@brief Configuración común de las pruebas.
@author Santiago Caicedo
"""

import os

import matplotlib

# Las pruebas de la ventana corren sin pantalla (también en GitHub Actions).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Dibujar sin ventanas: las pruebas corren en servidores sin pantalla.
matplotlib.use("Agg")
