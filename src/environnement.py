"""
BAZIZ Badis et GRAZIANI Olivier
"""
from creatures.plantes import Plante
import numpy as np
from settings import *
from creatures.animaux import Predateur, Proie
import sqlite3
import json

class Monde:
    temp_optimale = 25
    humidite_optimale = 48
    
    def __init__(self, predateurs: list, proies: list, plantes: list, temperature=10, humidite=4, nom=''):
        self.nom = nom
        self.predateurs = predateurs
        self.proies = proies
        self.plantes = plantes

        self.proies_mortes = []
        self.predateurs_morts = []

        self.temperature = temperature
        self.humidite = humidite

        self.next_temperature = temperature
        self.next_humidite = humidite
        self.ajoute_predateurs = 0
        self.ajoute_proies = 0

        self.nombre_plantes = round(
            max(0, (1 - abs(self.temperature - Monde.temp_optimale)/50) * 
                (1 - abs(self.humidite - Monde.humidite_optimale)/100) * 100)
                )
        
    def pousse_plantes(self):
        for _ in range(self.nombre_plantes):
            x = np.random.uniform(0, WIDTH)
            y = np.random.uniform(0, HEIGHT)
            self.plantes.append(Plante(x, y))

    def generation_suivante(self):
        preds = self.predateurs + self.predateurs_morts
        nouveaux_preds = selection(preds)

        proies = self.proies + self.proies_mortes
        nouvelles_proies = selection(proies)

        self.proies = nouvelles_proies
        self.predateurs = nouveaux_preds

        self.proies_mortes = []
        self.predateurs_morts = []

        self.plantes = []
        self.pousse_plantes()

        self.temperature = self.next_temperature
        self.humidite = self.next_humidite

        for _ in range(self.add_predateurs):
            x = np.random.uniform(0, WIDTH)
            y = np.random.uniform(0, HEIGHT)
            self.predateurs.append(Predateur(x, y))

        for _ in range(self.add_proies):
            x = np.random.uniform(0, WIDTH)
            y = np.random.uniform(0, HEIGHT)
            self.proies.append(Proie(x, y))

        self.add_predateurs = 0
        self.add_proies = 0

        self.nombre_plantes = round(
            max(0, (1 - abs(self.temperature - Monde.temp_optimale)/50) *
                (1 - abs(self.humidite - Monde.humidite_optimale)/100) * 100)
        )

    def update(self):
        for predateur in self.predateurs:
            predateur.update(self)

        for proie in self.proies:
            proie.update(self)

        self.proies_mortes += [p for p in self.proies if not p.en_vie]
        self.proies = [p for p in self.proies if p.en_vie]

        self.predateurs_morts += [p for p in self.predateurs if not p.en_vie]
        self.predateurs = [p for p in self.predateurs if p.en_vie]


def selection(animaux):
    generation_suivante = []
    animaux_tries = sorted(animaux, key=lambda a: a.temps_vie + a.nourriture_mangee, reverse=True)
    for animal in animaux_tries[:10]:
        if animal.en_vie or animal.nourriture_mangee >= 2:
            generation_suivante.append(animal)
            for _ in range(animal.nourriture_mangee//2):
                x = np.random.uniform(0, WIDTH)
                y = np.random.uniform(0, HEIGHT)
                mutation = (
                    max(0.5, np.random.normal(animal.vitesse, 0.5)),
                    max(30,  np.random.normal(animal.fov_distance, 0.5)),
                    max(1,   np.random.normal(animal.taille, 0.5))
                )
                enfant = Predateur(x, y) if isinstance(animal, Predateur) else Proie(x, y)
                enfant.vitesse, enfant.fov_distance, enfant.taille = mutation
                generation_suivante.append(enfant)
    return generation_suivante[:200]


# ══════════════════════════════════════════════════════════════════════════════
#  SAUVEGARDE / CHARGEMENT
# ══════════════════════════════════════════════════════════════════════════════

def init_bdd_monde():
    """Crée la table de sauvegarde des simulations si elle n'existe pas."""
    conn = sqlite3.connect('bdd.db')
    cur  = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS simulations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nom         TEXT,
            generation  INTEGER,
            temperature REAL,
            humidite    REAL,
            predateurs  TEXT,
            proies      TEXT,
            plantes     TEXT,
            date        TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')
    conn.commit()
    conn.close()


def _animal_to_dict(animal):
    return {
        "x":               float(animal.position[0]),
        "y":               float(animal.position[1]),
        "vitesse":         float(animal.vitesse),
        "fov_distance":    float(animal.fov_distance),
        "fov_angle":       float(animal.fov_angle),
        "taille":          float(animal.taille),
        "energie":         float(animal.energie),
        "temps_vie":       float(animal.temps_vie),
        "nourriture_mangee": int(animal.nourriture_mangee),
        "direction":       [float(animal.direction[0]), float(animal.direction[1])],
    }


def _dict_to_animal(d, cls):
    a = cls(d["x"], d["y"])
    a.vitesse          = d["vitesse"]
    a.fov_distance     = d["fov_distance"]
    a.fov_angle        = d["fov_angle"]
    a.taille           = d["taille"]
    a.energie          = d["energie"]
    a.temps_vie        = d["temps_vie"]
    a.nourriture_mangee = d.get("nourriture_mangee", 0)
    a.direction        = np.array(d["direction"], dtype=float)
    return a


def _plante_to_dict(plante):
    return {
        "x":         float(plante.position[0]),
        "y":         float(plante.position[1]),
        "nutriments": float(plante.nutriments),
        "etat":      plante.etat,
    }


def _dict_to_plante(d):
    p = Plante(d["x"], d["y"])
    p.nutriments = d["nutriments"]
    p.etat       = d["etat"]
    return p


def sauvegarder_simulation(monde, generation, nom=""):
    """Sérialise l'état complet du monde et le stocke en BDD."""
    init_bdd_monde()
    conn = sqlite3.connect('bdd.db')
    cur  = conn.cursor()
    cur.execute('''
        INSERT INTO simulations (nom, generation, temperature, humidite, predateurs, proies, plantes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        nom,
        generation,
        monde.temperature,
        monde.humidite,
        json.dumps([_animal_to_dict(a) for a in monde.predateurs]),
        json.dumps([_animal_to_dict(a) for a in monde.proies]),
        json.dumps([_plante_to_dict(p) for p in monde.plantes]),
    ))
    conn.commit()
    conn.close()
    print(f"[BDD] Simulation '{nom}' (génération {generation}) sauvegardée.")


def charger_simulation(sim_id):
    """
    Charge une simulation depuis la BDD.
    Retourne (monde, generation) ou (None, None) si introuvable.
    """
    init_bdd_monde()
    conn = sqlite3.connect('bdd.db')
    cur  = conn.cursor()
    cur.execute("SELECT generation, temperature, humidite, predateurs, proies, plantes FROM simulations WHERE id=?", (sim_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None, None

    generation, temperature, humidite, preds_json, proies_json, plantes_json = row

    predateurs = [_dict_to_animal(d, Predateur) for d in json.loads(preds_json)]
    proies     = [_dict_to_animal(d, Proie)     for d in json.loads(proies_json)]
    plantes    = [_dict_to_plante(d)             for d in json.loads(plantes_json)]

    monde = Monde(predateurs, proies, plantes, temperature=temperature, humidite=humidite)
    return monde, generation


def lister_sauvegardes():
    """Retourne la liste de toutes les sauvegardes : [(id, nom, generation, temperature, humidite, date), ...]"""
    init_bdd_monde()
    conn = sqlite3.connect('bdd.db')
    cur  = conn.cursor()
    cur.execute("SELECT id, nom, generation, temperature, humidite, date FROM simulations ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows