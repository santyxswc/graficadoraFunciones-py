"""
@file conftest.py
@brief Configuración común de las pruebas.
@author Santiago Caicedo
"""

import matplotlib

# Dibujar sin ventanas: las pruebas corren en servidores sin pantalla.
matplotlib.use("Agg")
