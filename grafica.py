import matplotlib.pyplot as plt
import networkx as nx

# Definir el conjunto A y crear un grafo dirigido
A = [2, 3, 5, 6, 10, 26]
G = nx.DiGraph()

# Agregar nodos al grafo
G.add_nodes_from(A)

# Agregar aristas basadas en la relación R: y = 2x + 1
for x in A:
    y = 2 * x + 1
    if y in A:
        G.add_edge(x, y)

# Dibujar el grafo
pos = nx.spring_layout(G)  # Define la disposición del grafo
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=700, edge_color='k', linewidths=1, font_size=15)

# Mostrar el dígrafo
plt.show()
