"""
@file relaciones.py
@brief Relaciones binarias definidas por una regla sobre un conjunto finito.
@author Santiago Caicedo
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class RelacionBinaria:
    """
    Relación ``R`` sobre un conjunto ``A``: ``x R y`` si ``y = regla(x)`` y ``y`` está en ``A``.

    Ejemplo::

        >>> r = RelacionBinaria.desde_regla([2, 3, 5, 6, 10, 26], lambda x: 2 * x + 1)
        >>> sorted(r.pares)
        [(2, 5)]
    """

    conjunto: tuple[int, ...]
    pares: frozenset[tuple[int, int]] = field(default_factory=frozenset)

    @classmethod
    def desde_regla(cls, conjunto: Iterable[int], regla: Callable[[np.ndarray], np.ndarray]) -> RelacionBinaria:
        """
        Construye la relación aplicando la regla a cada elemento.

        @param conjunto Elementos enteros de ``A`` (se ignoran repetidos).
        @param regla Función que da la imagen de cada ``x``.
        @return La relación con todos los pares ``(x, regla(x))`` que caen dentro de ``A``.
        @throws ValueError si el conjunto está vacío.
        """
        elementos = tuple(sorted(set(conjunto)))
        if not elementos:
            raise ValueError("El conjunto no puede estar vacio.")
        miembros = set(elementos)
        imagenes = np.asarray(regla(np.array(elementos, dtype=float)), dtype=float)
        pares = set()
        for x, y in zip(elementos, imagenes, strict=True):
            if math.isfinite(y) and math.isclose(y, round(y), abs_tol=1e-9) and int(round(y)) in miembros:
                pares.add((x, int(round(y))))
        return cls(elementos, frozenset(pares))

    def es_reflexiva(self) -> bool:
        """@return True si todo ``x`` está relacionado consigo mismo."""
        return all((x, x) in self.pares for x in self.conjunto)

    def es_simetrica(self) -> bool:
        """@return True si ``x R y`` implica ``y R x``."""
        return all((y, x) in self.pares for x, y in self.pares)

    def es_antisimetrica(self) -> bool:
        """@return True si ``x R y`` y ``y R x`` implican ``x = y``."""
        return all(x == y or (y, x) not in self.pares for x, y in self.pares)

    def es_transitiva(self) -> bool:
        """@return True si ``x R y`` y ``y R z`` implican ``x R z``."""
        return all((x, z) in self.pares for x, y in self.pares for w, z in self.pares if y == w)

    def propiedades(self) -> dict[str, bool]:
        """@return Las cuatro propiedades clásicas con su valor."""
        return {
            "reflexiva": self.es_reflexiva(),
            "simetrica": self.es_simetrica(),
            "antisimetrica": self.es_antisimetrica(),
            "transitiva": self.es_transitiva(),
        }
