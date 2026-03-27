"""
BAZIZ Badis et GRAZIANI Olivier
"""

import numpy as np

class Plante():
    def __init__(self, x, y):
        self.position = np.array([x, y], dtype=float)
        self.nutriments = np.random.poisson(10)
        self.etat = True # True : en vie, False: consommée

    def consommation(self):
        self.etat = False

    def update(self):
        return self.etat