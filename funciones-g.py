import numpy as np

import matplotlib.pyplot as plt

# Definir la función g(x)
def g(x):
    return 1 - np.abs(x-3)**(2/3)

# Creacion de un rango de valores de x
x = np.linspace(-5, 4, 400)
y = g(x)

# Crear la gráfica
plt.plot(x, y, label='g(x) = 1 - (x-3)^(2/3)')
plt.scatter([3, -5, 4], [g(3), g(-5), g(4)], color='red')  # Puntos críticos y extremos
plt.annotate('Máx. absoluto (3, 1)', xy=(3, 1), xytext=(0, 1.5),
             arrowprops=dict(facecolor='black', shrink=0.05))
plt.annotate('Mín. absoluto (-5, -3)', xy=(-5, -3), xytext=(-3, -2.5),
             arrowprops=dict(facecolor='black', shrink=0.05))
plt.annotate('g(4) = 0', xy=(4, 0), xytext=(2, -0.5),
             arrowprops=dict(facecolor='black', shrink=0.05))

# Configuracion de la gráfica
plt.title('Gráfica de g(x) = 1 - (x-3)^(2/3)')
plt.xlabel('x')
plt.ylabel('g(x)')
plt.legend()
plt.grid(True)
plt.axhline(0, color='black',linewidth=0.5)
plt.axvline(0, color='black',linewidth=0.5)
plt.show()
