"""
BAZIZ Badis et GRAZIANI Olivier
"""

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800

WIDTH, HEIGHT = 800, 600
BLEU = (50, 150, 255)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS_SURVOL = (200, 200, 200)
GRIS_SAISIE = (220, 220, 220)
VERT_ACTIF = (100, 255, 100)

pygame.init()

police_titre = pygame.font.SysFont("Century Gothic", 44, bold=True)
police_bouton = pygame.font.SysFont("Century Gothic", 26, bold=True)
police_saisie = pygame.font.SysFont("Century Gothic", 16)
