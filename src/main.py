"""
BAZIZ Badis et GRAZIANI Olivier
main.py — SCADEN  (Simulation Chaîne Alimentaire Dans un Environnement Naturel)
Point d'entrée.
"""

import sys
import os
import sqlite3
import math

import pygame
import numpy as np

BASE_DIR = os.path.dirname(__file__)
sys.path.append(BASE_DIR)

from settings import *
from creatures.animaux import Animaux, Predateur, Proie
from creatures.plantes import Plante
from environnement import (Monde, sauvegarder_simulation,
                            charger_simulation, lister_sauvegardes, init_bdd_monde)

# ── Palette ───────────────────────────────────────────────────────────────────
VERT_PLANTE  = (80,  200,  80)
ROUGE_PRED   = (220,  60,  60)
BLEU_PROIE   = (60,  140, 220)
FOND_SIMU    = (20,   35,  20)
FOND_PANEL   = (30,   30,  40)
FOND_CMD     = (25,   25,  35)
BORDURE      = (80,   80, 100)

ZONE_SIMU  = pygame.Rect(0,      0,      WIDTH,              HEIGHT)
ZONE_STATS = pygame.Rect(WIDTH,  0,      SCREEN_WIDTH-WIDTH, HEIGHT)
ZONE_CMD   = pygame.Rect(0,      HEIGHT, SCREEN_WIDTH,       SCREEN_HEIGHT-HEIGHT)


# ══════════════════════════════════════════════════════════════════════════════
#  BASE DE DONNÉES (noms de simulations — table legacy du collègue)
# ══════════════════════════════════════════════════════════════════════════════

def init_bdd():
    conn = sqlite3.connect('bdd.db')
    cur  = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Sauvegarde (
                        sauvegarde_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        text TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS generations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        generation   INTEGER,
                        nb_predateurs INTEGER,
                        nb_proies    INTEGER,
                        vitesse_pred  REAL,
                        vitesse_proie REAL)''')
    conn.commit()
    conn.close()
    init_bdd_monde()


# ══════════════════════════════════════════════════════════════════════════════
#  UTILITAIRES DESSIN
# ══════════════════════════════════════════════════════════════════════════════

def draw_text(surface, texte, police, couleur, x, y):
    surf = police.render(texte, True, couleur)
    rect = surf.get_rect(center=(x, y))
    surface.blit(surf, rect)


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
    pos  = animal.position
    direction_angle = math.atan2(animal.direction[1], animal.direction[0])
    start_angle = direction_angle - animal.fov_angle / 2
    end_angle   = direction_angle + animal.fov_angle / 2
    points = [tuple(pos)]
    for i in range(31):
        angle = start_angle + (end_angle - start_angle) * (i / 30)
        points.append((pos[0] + math.cos(angle) * animal.fov_distance,
                       pos[1] + math.sin(angle) * animal.fov_distance))
    pygame.draw.polygon(surf, color, points)
    screen.blit(surf, (0, 0))


def trouver_animal_clique(monde, pos, tolerance=15):
    mx, my = pos
    meilleur, dist_min = None, tolerance
    for a in monde.predateurs + monde.proies:
        d = np.linalg.norm(a.position - np.array([mx, my]))
        if d < dist_min:
            dist_min = d
            meilleur = a
    return meilleur


# ══════════════════════════════════════════════════════════════════════════════
#  WIDGET SLIDER RÉUTILISABLE
# ══════════════════════════════════════════════════════════════════════════════

class Slider:
    """Slider horizontal simple."""
    def __init__(self, x, y, width, val_min, val_max, valeur_initiale, label, entier=False):
        self.x, self.y, self.w = x, y, width
        self.val_min  = val_min
        self.val_max  = val_max
        self.entier   = entier
        self.label    = label
        self.h        = 5
        self.r        = 10
        self.dragging = False
        self.set_valeur(valeur_initiale)

    def set_valeur(self, v):
        v = max(self.val_min, min(self.val_max, v))
        self.valeur = int(v) if self.entier else v
        self.handle_x = self.x + (v - self.val_min) / (self.val_max - self.val_min) * self.w

    @property
    def handle_pos(self):
        return (int(self.handle_x), self.y + self.h // 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            dist = ((mx - self.handle_x)**2 + (my - (self.y + self.h//2))**2)**0.5
            if dist <= self.r:
                self.dragging = True
        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        if event.type == pygame.MOUSEMOTION and self.dragging:
            nx = max(self.x, min(event.pos[0], self.x + self.w))
            self.handle_x = nx
            raw = self.val_min + (nx - self.x) / self.w * (self.val_max - self.val_min)
            self.valeur = int(round(raw)) if self.entier else raw

    def draw(self, surface):
        # Piste
        pygame.draw.rect(surface, GRIS_SURVOL,
                         (self.x, self.y, self.w, self.h), border_radius=3)
        # Portion remplie
        filled_w = int(self.handle_x - self.x)
        if filled_w > 0:
            pygame.draw.rect(surface, VERT_ACTIF,
                             (self.x, self.y, filled_w, self.h), border_radius=3)
        # Handle
        pygame.draw.circle(surface, BLANC, self.handle_pos, self.r)
        pygame.draw.circle(surface, NOIR,  self.handle_pos, self.r, 2)
        # Labels
        draw_text(surface, self.label,
                  police_saisie, BLANC,
                  self.x + self.w // 2, self.y - 22)
        val_str = str(self.valeur) if self.entier else f"{self.valeur:.0f}"
        draw_text(surface, f"Valeur : {val_str}",
                  police_saisie, BLANC,
                  self.x + self.w // 2, self.y + 25)


# ══════════════════════════════════════════════════════════════════════════════
#  PANNEAUX SIMULATION
# ══════════════════════════════════════════════════════════════════════════════

def dessiner_panneau_stats(ecran, monde, generation, animal_sel):
    pygame.draw.rect(ecran, FOND_PANEL, ZONE_STATS)
    pygame.draw.line(ecran, BORDURE, (WIDTH, 0), (WIDTH, HEIGHT), 2)

    cx = WIDTH + (SCREEN_WIDTH - WIDTH) // 2
    y  = 25

    draw_text(ecran, "── STATS ──",               police_saisie,  BLANC,       cx, y); y += 35
    draw_text(ecran, f"Génération {generation}",  police_bouton,  BLANC,       cx, y); y += 30
    draw_text(ecran, f"{len(monde.predateurs)+len(monde.proies)} animaux",
              police_saisie, BLANC, cx, y); y += 40

    draw_text(ecran, f"Prédateurs : {len(monde.predateurs)}", police_saisie, ROUGE_PRED,  cx, y); y += 25
    draw_text(ecran, f"Proies     : {len(monde.proies)}",     police_saisie, BLEU_PROIE,  cx, y); y += 25
    draw_text(ecran, f"Plantes    : {len(monde.plantes)}",    police_saisie, VERT_PLANTE, cx, y); y += 35

    draw_text(ecran, f"Temp  : {int(monde.temperature)}°C", police_saisie, BLANC, cx, y); y += 22
    draw_text(ecran, f"Humid : {int(monde.humidite)}%",     police_saisie, BLANC, cx, y); y += 40

    if animal_sel:
        a = animal_sel
        couleur_type = ROUGE_PRED if isinstance(a, Predateur) else BLEU_PROIE
        type_str     = "PRÉDATEUR"  if isinstance(a, Predateur) else "PROIE"
        draw_text(ecran, "── Sélection ──",             police_saisie, BLANC,        cx, y); y += 28
        draw_text(ecran, type_str,                      police_bouton, couleur_type, cx, y); y += 28
        draw_text(ecran, f"Vitesse : {a.vitesse:.2f}",  police_saisie, BLANC,        cx, y); y += 22
        draw_text(ecran, f"Énergie : {int(a.energie)}", police_saisie, BLANC,        cx, y); y += 22
        draw_text(ecran, f"Taille  : {a.taille:.1f}",   police_saisie, BLANC,        cx, y); y += 22
        draw_text(ecran, f"FOV     : {int(a.fov_distance)}", police_saisie, BLANC,   cx, y)
    else:
        draw_text(ecran, "Cliquez sur un animal", police_saisie, BLANC, cx, y); y += 22
        draw_text(ecran, "pour le sélectionner",  police_saisie, BLANC, cx, y)


def dessiner_panneau_cmd(ecran, en_pause, pos_souris,
                          btn_pause, btn_relancer, btn_vitesse, btn_sauver,
                          vitesse_actuelle):
    pygame.draw.rect(ecran, FOND_CMD, ZONE_CMD)
    pygame.draw.line(ecran, BORDURE, (0, HEIGHT), (SCREEN_WIDTH, HEIGHT), 2)

    couleur_vit = (255, 200, 50) if vitesse_actuelle > 1 else BLANC
    for btn, label in [
        (btn_pause,    "PAUSE" if not en_pause else "▶  PLAY"),
        (btn_relancer, "RELANCER"),
        (btn_vitesse,  f"x{vitesse_actuelle}"),
        (btn_sauver,   "SAUVER"),
    ]:
        survol = btn.collidepoint(pos_souris)
        pygame.draw.rect(ecran, (80,80,110) if survol else (50,50,70), btn, border_radius=10)
        pygame.draw.rect(ecran, BORDURE, btn, 2, border_radius=10)
        draw_text(ecran, label, police_saisie,
                  couleur_vit if btn is btn_vitesse else BLANC,
                  btn.centerx, btn.centery)


def dessiner_simulation(ecran, monde, generation, show_fov):
    pygame.draw.rect(ecran, FOND_SIMU, ZONE_SIMU)
    ecran.blit(police_saisie.render(f"Génération n°{generation}  |  V: champ vision", True, BLANC), (10, 8))

    for p in monde.plantes:
        x, y = int(p.position[0]), int(p.position[1])
        if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
            pygame.draw.circle(ecran, VERT_PLANTE, (x, y), 3)

    if show_fov:
        for proie in monde.proies:
            champ_vision(ecran, proie, monde)
        for pred in monde.predateurs:
            champ_vision(ecran, pred, monde)

    for proie in monde.proies:
        r  = max(2, int(proie.taille))
        pi = proie.position.astype(int)
        pygame.draw.circle(ecran, (0,0,0),    (pi[0]+2, pi[1]+2), r)
        pygame.draw.circle(ecran, BLEU_PROIE, pi, r)

    for pred in monde.predateurs:
        r  = max(2, int(pred.taille))
        pi = pred.position.astype(int)
        pygame.draw.circle(ecran, (0,0,0),   (pi[0]+2, pi[1]+2), r)
        pygame.draw.circle(ecran, ROUGE_PRED, pi, r)


# ══════════════════════════════════════════════════════════════════════════════
#  FACTORY MONDE
# ══════════════════════════════════════════════════════════════════════════════

def _nouveau_monde(temperature, humidite, nb_pred=10, nb_proie=10, n=''):
    m = Monde(
        [Predateur(np.random.uniform(0, WIDTH), np.random.uniform(0, HEIGHT)) for _ in range(nb_pred)],
        [Proie   (np.random.uniform(0, WIDTH), np.random.uniform(0, HEIGHT)) for _ in range(nb_proie)],
        [],
        temperature=temperature,
        humidite=humidite,
        nom=n
    )
    m.pousse_plantes()
    return m


# ══════════════════════════════════════════════════════════════════════════════
#  MENU PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def menu_principal(ecran):
    path_image = os.path.join(BASE_DIR, 'Assets', 'fond.jpg')
    try:
        fond = pygame.transform.scale(pygame.image.load(path_image), (WIDTH, HEIGHT))
    except Exception:
        fond = None

    clock = pygame.time.Clock()
    while True:
        if fond:
            ecran.blit(fond, (0, 0))
        else:
            ecran.fill((30, 30, 30))

        pos_souris = pygame.mouse.get_pos()

        btn_jouer    = pygame.Rect(0,0,300,70); btn_jouer.center    = (WIDTH//2, 280)
        btn_charger  = pygame.Rect(0,0,300,70); btn_charger.center  = (WIDTH//2, 380)
        btn_quitter  = pygame.Rect(0,0,300,70); btn_quitter.center  = (WIDTH//2, 480)

        draw_text(ecran, "SCADEN", police_titre, BLANC, WIDTH//2, 100)

        for btn, label in [(btn_jouer,"START"), (btn_charger,"CHARGER"), (btn_quitter,"QUITTER")]:
            coul = GRIS_SURVOL if btn.collidepoint(pos_souris) else BLANC
            pygame.draw.rect(ecran, coul, btn, border_radius=10)
            pygame.draw.rect(ecran, NOIR, btn, 3, border_radius=10)
            draw_text(ecran, label, police_bouton, NOIR, btn.centerx, btn.centery)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_jouer.collidepoint(event.pos):
                    return "start"
                if btn_charger.collidepoint(event.pos):
                    return "charger"
                if btn_quitter.collidepoint(event.pos):
                    pygame.quit(); sys.exit()


# ══════════════════════════════════════════════════════════════════════════════
#  MENU PARAMÉTRAGE
# ══════════════════════════════════════════════════════════════════════════════

def menu_parametrage(ecran):
    """
    Retourne (temperature, humidite, nb_pred, nb_proie) ou None si annulé.
    """
    col1 = WIDTH // 5
    col2 = 2 * WIDTH // 5
    col3 = 3 * WIDTH // 5
    col4 = 4 * WIDTH // 5
    sy   = HEIGHT // 2

    sliders = [
        Slider(col1 - 60, sy, 120,   0, 100, 50,  "Température", entier=True),
        Slider(col2 - 60, sy, 120,   0, 100, 50,  "Humidité",    entier=True),
        Slider(col3 - 60, sy, 120,   0,  30,  10, "Prédateurs",  entier=True),
        Slider(col4 - 60, sy, 120,   0,  30,  10, "Proies",      entier=True),
    ]

    input_rect  = pygame.Rect(0,0,200,25); input_rect.center = (WIDTH//2, 160)
    texte_saisi = ""
    actif       = False

    ecran_para = pygame.display.set_mode((WIDTH, HEIGHT))
    clock      = pygame.time.Clock()

    while True:
        ecran_para.fill((50, 50, 50))
        draw_text(ecran_para, "PARAMETRAGE DE LA SIMU",         police_titre,  BLANC, WIDTH//2, 50)
        draw_text(ecran_para, "Nom de la simulation (Entrée pour valider)", police_saisie, BLANC, WIDTH//2, 120)
        draw_text(ecran_para, "ÉCHAP pour revenir",             police_saisie, BLANC, WIDTH//2, HEIGHT - 40)

        for s in sliders:
            s.draw(ecran_para)

        btn_lancer = pygame.Rect(WIDTH//2-100, HEIGHT-110, 200, 50)
        pygame.draw.rect(ecran_para, VERT_ACTIF, btn_lancer, border_radius=10)
        draw_text(ecran_para, "Lancer la Simu", police_bouton, NOIR, btn_lancer.centerx, btn_lancer.centery)

        # Barre de saisie
        coul_barre = VERT_ACTIF if actif else GRIS_SAISIE
        pygame.draw.rect(ecran_para, coul_barre, input_rect)
        pygame.draw.rect(ecran_para, NOIR,       input_rect, 2)
        ecran_para.blit(police_saisie.render(texte_saisi, True, NOIR), (input_rect.x+5, input_rect.y+2))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            for s in sliders:
                s.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if actif:
                    if event.key == pygame.K_RETURN and texte_saisi.strip():
                        conn = sqlite3.connect('bdd.db')
                        conn.execute("INSERT INTO Sauvegarde (text) VALUES (?)", (texte_saisi,))
                        conn.commit(); conn.close()
                        texte_saisi = ""
                    elif event.key == pygame.K_BACKSPACE:
                        texte_saisi = texte_saisi[:-1]

            if event.type == pygame.TEXTINPUT and actif:
                texte_saisi += event.text

            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_lancer.collidepoint(event.pos):
                    return (sliders[0].valeur, sliders[1].valeur,
                            sliders[2].valeur, sliders[3].valeur, texte_saisi)
                actif = input_rect.collidepoint(event.pos)


# ══════════════════════════════════════════════════════════════════════════════
#  MENU CHARGEMENT
# ══════════════════════════════════════════════════════════════════════════════

def menu_chargement(ecran):
    """
    Affiche la liste des sauvegardes et retourne (monde, generation) ou (None, None).
    """
    ecran_ch = pygame.display.set_mode((WIDTH, HEIGHT))
    clock    = pygame.time.Clock()
    scroll   = 0
    ligne_h  = 40
    marge    = 60

    while True:
        ecran_ch.fill((40, 40, 50))
        draw_text(ecran_ch, "CHARGER UNE SIMULATION", police_titre, BLANC, WIDTH//2, 40)
        draw_text(ecran_ch, "ÉCHAP pour revenir",     police_saisie, BLANC, WIDTH//2, HEIGHT-30)

        sauvegardes = lister_sauvegardes()  # [(id, nom, gen, temp, humid, date), ...]

        if not sauvegardes:
            draw_text(ecran_ch, "Aucune sauvegarde disponible.", police_bouton, GRIS_SURVOL, WIDTH//2, HEIGHT//2)
        else:
            y_start = 90
            btn_rects = []
            for i, (sid, nom, gen, temp, humid, date) in enumerate(sauvegardes):
                y = y_start + i * ligne_h - scroll
                if y < 80 or y > HEIGHT - 50:
                    btn_rects.append(None)
                    continue
                label = f"#{sid}  {nom or '(sans nom)'}  |  Gén.{gen}  T:{int(temp)}°  H:{int(humid)}%  —  {date}"
                rect  = pygame.Rect(marge, y - 15, WIDTH - 2*marge, 32)
                survol = rect.collidepoint(pygame.mouse.get_pos())
                pygame.draw.rect(ecran_ch, (70,70,100) if survol else (50,50,70), rect, border_radius=8)
                pygame.draw.rect(ecran_ch, BORDURE, rect, 1, border_radius=8)
                surf = police_saisie.render(label, True, BLANC)
                ecran_ch.blit(surf, (marge + 8, y - 8))
                btn_rects.append(rect)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None, None
            if event.type == pygame.MOUSEWHEEL:
                scroll = max(0, scroll - event.y * ligne_h)
            if event.type == pygame.MOUSEBUTTONDOWN and sauvegardes:
                for i, rect in enumerate(btn_rects):
                    if rect and rect.collidepoint(event.pos):
                        sid = sauvegardes[i][0]
                        monde, generation = charger_simulation(sid)
                        if monde:
                            return monde, generation

def dessiner_menu_pause(screen, sliders):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    cx = SCREEN_WIDTH // 2

    draw_text(screen, "MENU PAUSE", police_titre, BLANC, cx, 80)
    draw_text(screen, "Paramètres prochaine génération", police_saisie, BLANC, cx, 140)

    # Dessin sliders
    for s in sliders:
        s.draw(screen)

    draw_text(screen, "Appuyez sur la touche pause ou P pour reprendre", police_saisie, BLANC, cx, SCREEN_HEIGHT - 60)

# ══════════════════════════════════════════════════════════════════════════════
#  BOUCLE DE SIMULATION
# ══════════════════════════════════════════════════════════════════════════════

def simulation_loop(monde, generation=1):
    ecran_simu = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("SCADEN – Simulation")

    temperature = monde.temperature
    humidite    = monde.humidite
    nom = monde.nom

    clock         = pygame.time.Clock()
    en_cours      = True
    en_pause      = False
    ticks_par_gen = 300 # fonctionnalité désactivée
    tick_count    = 0
    dt            = 0
    animal_sel    = None
    show_fov      = True
    VITESSES      = [1, 2, 5, 10]
    idx_vitesse   = 0

    btn_w, btn_h = 120, 55
    btn_y = HEIGHT + (SCREEN_HEIGHT - HEIGHT) // 2
    btn_pause    = pygame.Rect(0,0,btn_w,btn_h); btn_pause.center    = (SCREEN_WIDTH//5,     btn_y)
    btn_relancer = pygame.Rect(0,0,btn_w,btn_h); btn_relancer.center = (2*SCREEN_WIDTH//5,   btn_y)
    btn_vitesse  = pygame.Rect(0,0,btn_w,btn_h); btn_vitesse.center  = (3*SCREEN_WIDTH//5,   btn_y)
    btn_sauver   = pygame.Rect(0,0,btn_w,btn_h); btn_sauver.center   = (4*SCREEN_WIDTH//5,   btn_y)
    sliders_next = [
        Slider(WIDTH + 50, 350, 150, 0, 100, monde.temperature, "Temp Next", True),
        Slider(WIDTH + 50, 420, 150, 0, 100, monde.humidite, "Hum Next", True),
        Slider(WIDTH + 50, 490, 150, 0, 20, 0, "Ajout Pred", True),
        Slider(WIDTH + 50, 560, 150, 0, 20, 0, "Ajout Proies", True),
        ]
    
    menu_pause_actif = False

    while en_cours:
        pos_souris = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    en_cours = False
                if event.key in (pygame.K_SPACE, pygame.K_p):
                    en_pause = not en_pause
                    menu_pause_actif = en_pause
                if event.key == pygame.K_n:
                    monde.generation_suivante()
                    generation += 1
                    tick_count  = 0
                    animal_sel  = None
                if event.key == pygame.K_v:
                    show_fov = not show_fov

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_pause.collidepoint(event.pos):
                    en_pause = not en_pause
                    menu_pause_actif = en_pause
                elif btn_vitesse.collidepoint(event.pos):
                    idx_vitesse = (idx_vitesse + 1) % len(VITESSES)
                elif btn_relancer.collidepoint(event.pos):
                    monde      = _nouveau_monde(temperature, humidite, n=nom)
                    generation = 1
                    tick_count = 0
                    animal_sel = None
                elif btn_sauver.collidepoint(event.pos):
                    sauvegarder_simulation(monde, generation, nom)
                elif ZONE_SIMU.collidepoint(event.pos):
                    animal_sel = trouver_animal_clique(monde, event.pos)
            if menu_pause_actif:
                for s in sliders_next:
                    s.handle_event(event)
                continue

        # ── Logique ───────────────────────────────────────────────────────────

        if not en_pause:
            monde.next_temperature = sliders_next[0].valeur
            monde.next_humidite    = sliders_next[1].valeur
            monde.add_predateurs   = sliders_next[2].valeur
            monde.add_proies       = sliders_next[3].valeur
            for _ in range(VITESSES[idx_vitesse]):
                monde.update()

                for a in monde.predateurs + monde.proies:
                    a.temps_vie += dt

                monde.plantes = [pl for pl in monde.plantes if pl.update()]
                tick_count += 1

                tous_morts = len(monde.predateurs) == 0 and len(monde.proies) == 0
                if tous_morts:
                    generation += 1
                    tick_count  = 0
                    animal_sel  = None
                    monde.generation_suivante()
                    break

        # ── Dessin ────────────────────────────────────────────────────────────
        ecran_simu.fill(NOIR)

        dessiner_simulation(ecran_simu, monde, generation, show_fov)
        dessiner_panneau_cmd(ecran_simu, en_pause, pos_souris,
                              btn_pause, btn_relancer, btn_vitesse, btn_sauver,
                              VITESSES[idx_vitesse])
        dessiner_panneau_stats(ecran_simu, monde, generation, animal_sel)
        if menu_pause_actif:
            dessiner_menu_pause(ecran_simu, sliders_next)
        pygame.display.flip()
        dt = clock.tick(60) / 1000

    pygame.display.set_mode((WIDTH, HEIGHT))


# ══════════════════════════════════════════════════════════════════════════════
#  POINT D'ENTRÉE
# ══════════════════════════════════════════════════════════════════════════════

def main():
    pygame.init()
    init_bdd()

    ecran = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SCADEN")

    while True:
        action = menu_principal(ecran)

        if action == "start":
            resultat = menu_parametrage(ecran)
            if resultat is not None:
                temperature, humidite, nb_pred, nb_proie, nom = resultat
                monde = _nouveau_monde(temperature, humidite, nb_pred, nb_proie, n=nom)
                simulation_loop(monde, generation=1)

        elif action == "charger":
            monde, generation = menu_chargement(ecran)
            if monde is not None:
                simulation_loop(monde, generation)


if __name__ == "__main__":
    main()