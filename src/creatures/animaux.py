"""
BAZIZ Badis et GRAZIANI Olivier
"""

import numpy as np
from settings import *
from math import cos, sin, atan2, pi, radians
import noise

def rotation(vecteur: np.ndarray, theta: float):
    rotation_matrix = np.array([
        [cos(theta), -sin(theta)],
        [sin(theta),  cos(theta)]
    ])
    v = rotation_matrix @ vecteur
    norm = np.linalg.norm(v)
    if norm != 0:
        v = v / norm

    return v


class Animaux:
    def __init__(self, x: float, y: float):
        self.position = np.array([x, y], dtype=float)

        self.vitesse = max(0.5, np.random.uniform(0.5, 4))
        self.direction = np.array([1.0, 0.0], dtype=float)
        self.fov_angle = radians(90)
        self.fov_distance = 100  # + distance => + energie dépensée

        self.taille = max(2, np.random.uniform(2, 10))
        self.energie = 100  # énergie == 0 alors mort.
        self.en_vie = True
        
        self.temps_vie = 0
        self.nourriture_mangee = 0

        # Paramètres du bruit de perlin
        self.noise_offset = np.random.rand() * 1000
        self.noise_scale = 0.03
        self.max_turn = np.radians(8)

    def collisions(self):
        nx = self.position[0] + self.direction[0] * self.vitesse
        ny = self.position[1] + self.direction[1] * self.vitesse

        collision_x = not (0 <= nx <= WIDTH)
        collision_y = not (0 <= ny <= HEIGHT)

        if collision_x and collision_y:
            return (True, 'xy')
        elif collision_x:
            return (True, 'x')
        elif collision_y:
            return (True, 'y')
        else:
            return (False, None)
        
    def deplacement(self):
        col, dir = self.collisions()
        
        if col == True:
            if dir == 'xy':
                self.direction = -self.direction
            elif dir == 'x':
                self.position = np.array([self.position[0], self.position[1] + self.direction[1]*self.vitesse])
                self.tourner(rotation(self.direction, radians(180)*np.random.choice([1, -1])))
            elif dir == 'y':
                self.position = np.array([self.position[0] + self.direction[0]*self.vitesse, self.position[1]])
                self.tourner(rotation(self.direction, radians(180)*np.random.choice([1, -1])))
        else:        
            self.position += self.direction * self.vitesse

        self.energie -= (0.02 * self.taille + 0.05 * self.vitesse * self.taille + 0.0005 * self.fov_distance)*0.5
        
        if self.energie <= 0:
            self.en_vie = False

    def tourner(self, vecteur_cible: np.ndarray, max_turn=np.radians(10)):
        angle = atan2(vecteur_cible[1], vecteur_cible[0]) - atan2(self.direction[1], self.direction[0])
        angle = (angle + pi) % (2*pi) - pi

        if abs(angle) > max_turn:
            angle = max_turn if angle > 0 else -max_turn

        self.direction = rotation(self.direction, angle)

    def errance(self):
        """
        La fonction d'errance s'active quand l'animal n'est pas en état de repos, ni de chasse, ni de fuite.
        Sa direction varie avec un bruit aléatoire, et il cherche les ennemis ou la nourriture.
        """
        noise_val = noise.pnoise1(self.noise_offset)
        self.noise_offset += self.noise_scale

        angle_change = noise_val * self.max_turn

        vecteur_cible = rotation(self.direction, angle_change)
        self.tourner(vecteur_cible)

    def detection(self, objet):
        vect = objet.position - self.position
        distance = np.linalg.norm(vect)

        if distance > self.fov_distance:
            return False
            
        angle_cible = atan2(vect[1], vect[0])
        
        angle_dir = atan2(self.direction[1], self.direction[0])

        angle = angle_cible - angle_dir

        angle = abs((angle + pi) % (2*pi) - pi)
        return angle <= self.fov_angle / 2        


class Predateur(Animaux):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.fov_angle = radians(np.random.uniform(75, 130))
        self.fov_distance = 100

    def chasse(self, proie: Animaux):
        vect = proie.position - self.position
        norm = np.linalg.norm(vect)
        if norm != 0:
            vect = vect / norm

        if norm < self.taille:
            self.energie += proie.valeur_nutritive
            self.energie = min(self.energie, 200)
            proie.en_vie = False
            self.nourriture_mangee += 1

        self.tourner(vecteur_cible=vect)

    def update(self, monde):
        # Détéction
        proie_vue = None
        distance_min = float("inf")

        for proie in monde.proies:
            if self.detection(proie):
                d = np.linalg.norm(proie.position - self.position)
                if d < distance_min:
                    distance_min = d
                    proie_vue = proie

        # Décision
        if proie_vue:
            self.chasse(proie_vue)
        else:
            self.errance()

        # Action
        self.deplacement()


class Proie(Animaux):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.fov_angle = radians(np.random.uniform(180, 360))
        self.fov_distance = 75
        self.valeur_nutritive = 15*self.taille  # valeur nutritive dépend de la taille de l'animal

    def manger(self, plante):
        vect = plante.position - self.position
        norm = np.linalg.norm(vect)

        if norm <= self.taille:
            self.energie += plante.nutriments
            self.energie = min(self.energie, 150)
            plante.consommation()
            self.nourriture_mangee += 1

        if norm != 0:
            vect = vect / norm
        
        self.tourner(vecteur_cible=vect)

    def fuite(self, predateur: Animaux):
        vect = predateur.position - self.position
        norm = np.linalg.norm(vect)
        if norm != 0:
            vect = vect / norm
        vect = -vect

        self.tourner(vecteur_cible=vect)

    def update(self, monde):
        # Détection
        predateur_vu = None
        plante_vue = None
        distance_min_pred = float('inf')
        distance_min_plante = float('inf')

        for predateur in monde.predateurs:
            if self.detection(predateur):
                if np.linalg.norm(predateur.position - self.position) < distance_min_pred:
                    predateur_vu = predateur

        for plante in monde.plantes:
            if self.detection(plante):
                if np.linalg.norm(plante.position - self.position) < distance_min_plante:
                    plante_vue = plante

        # Décision (priorité fuite, puis manger, puis errer)
        if predateur_vu:
            self.fuite(predateur_vu)
        elif plante_vue:
            self.manger(plante_vue)
        else:
            self.errance()

        # Action
        self.deplacement()