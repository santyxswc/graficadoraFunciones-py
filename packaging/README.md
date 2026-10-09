# Empaquetado

`graficadora_gui.py` es el punto de entrada del ejecutable de escritorio. GitHub Actions
(flujo **Versión para Windows**) lo convierte en `Graficadora.exe` con PyInstaller:

```bash
pip install -e ".[gui]" pyinstaller
pyinstaller --noconfirm --windowed --name Graficadora packaging/graficadora_gui.py
```

El resultado queda en `dist/Graficadora/`: se puede copiar a cualquier computador con Windows y abrir
sin instalar Python.
