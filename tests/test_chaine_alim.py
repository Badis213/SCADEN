import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from creatures.animaux import Animaux, Predateur, Proie
from environnement import Monde

import pygame
import numpy as np
from settings import *
from math import sin, cos, atan2


monde = Monde(
    [Predateur(np.random.uniform(0, WIDTH), np.random.uniform(0, HEIGHT)) for _ in range(10)],
    [Proie(np.random.uniform(0, WIDTH), np.random.uniform(0, HEIGHT)) for _ in range(10)],
    []
)

monde.pousse_plantes()


def champ_vision(screen, animal, monde):

    color = (0, 255, 0, 20)

    if isinstance(animal, Predateur):
        for proie in monde.proies:
            if animal.detection(proie):
                color = (0, 0, 255, 20)
                break

    if isinstance(animal, Proie):
        for pred in monde.predateurs:
            if animal.detection(pred):
                color = (255, 0, 0, 20)
                break
        for plante in monde.plantes:
            if animal.detection(plante):
                color = (100, 100, 0, 30)

    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    pos = animal.position
    direction_angle = atan2(animal.direction[1], animal.direction[0])

    start_angle = direction_angle - animal.fov_angle / 2
    end_angle = direction_angle + animal.fov_angle / 2

    points = [pos]
    steps = 30

    for i in range(steps + 1):
        angle = start_angle + (end_angle - start_angle) * (i / steps)

        x = pos[0] + cos(angle) * animal.fov_distance
        y = pos[1] + sin(angle) * animal.fov_distance

        points.append((x, y))

    pygame.draw.polygon(surf, color, points)
    screen.blit(surf, (0, 0))


class Game:
    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Simulation chaîne alimentaire")
        self.font = pygame.font.SysFont('Arial', 24)  # police Arial, taille 24
        self.num_gen = 0

        self.clock = pygame.time.Clock()
        self.dt = 0

        self.running = True
        self.paused = False

    def run(self):

        global monde

        while self.running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused

                    if event.key == pygame.K_n:
                        monde.generation_suivante()

            self.screen.fill((30, 30, 30))
            text_surf = self.font.render(f"Génération : {self.num_gen}", True, (255, 255, 255))  # blanc
            self.screen.blit(text_surf, (10, 10))  # position x=10, y=10

            if not self.paused:

                # UPDATE MONDE
                monde.update()

                # temps de vie
                for a in monde.predateurs + monde.proies:
                    a.temps_vie += self.dt

                # plantes
                monde.plantes = [plante for plante in monde.plantes if plante.update()]

            # ----- DRAW -----

            for plante in monde.plantes:
                pygame.draw.rect(
                    self.screen,
                    (255, 100, 20),
                    pygame.Rect(int(plante.position[0]) - 3, int(plante.position[1]) - 3, 6, 6)
                )

            for proie in monde.proies:

                champ_vision(self.screen, proie, monde)

                pygame.draw.circle(
                    self.screen,
                    (0, 0, 0),
                    (proie.position[0] + 2, proie.position[1] + 2),
                    proie.taille
                )

                pygame.draw.circle(
                    self.screen,
                    "green",
                    proie.position.astype(int),
                    proie.taille
                )

            for pred in monde.predateurs:

                champ_vision(self.screen, pred, monde)

                pygame.draw.circle(
                    self.screen,
                    (0, 0, 0),
                    (pred.position[0] + 2, pred.position[1] + 2),
                    pred.taille
                )

                pygame.draw.circle(
                    self.screen,
                    "red",
                    pred.position.astype(int),
                    pred.taille
                )
            
            if len(monde.proies) == 0 or len(monde.predateurs) == 0:
                self.num_gen += 1
                monde.generation_suivante()

            pygame.display.flip()

            self.dt = self.clock.tick(60) / 1000

        pygame.quit()


if __name__ == '__main__':
    Game().run()