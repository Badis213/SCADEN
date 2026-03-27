# SCADEN — Simulation de Chaîne Alimentaire Dans un Environnement Naturel

Projet NSI — Terminale  
Simulation interactive d’un écosystème avec prédateurs, proies et plantes, incluant sélection naturelle et paramètres dynamiques.

---

## ⚙️ Version de Python

**Python 3.10 ou supérieur recommandé**  
(idéalement Python 3.13)

> ⚠️ Python 2 non supporté

---

## 📦 Installation

Installer les dépendances avec :

pip install -r requirements.txt

### Dépendances utilisées

| Bibliothèque | Rôle |
|---|---|
| pygame | Affichage graphique et interactions utilisateur |
| numpy | Calculs (positions, distances, vecteurs) |
| noise | Génération de comportements naturels |
| sqlite3 | Sauvegarde des simulations (inclus dans Python) |

---

## 📁 Structure du projet

.
│
├── main.py                  # Fichier principal (menus + simulation)
├── settings.py              # Constantes globales (taille, couleurs, polices)
├── environnement.py         # Classe Monde + logique de simulation
│
├── creatures/
│   ├── animaux.py           # Classes Animaux, Predateur, Proie
│   └── plantes.py           # Classe Plante
│
└── bdd.db                   # Base de données SQLite (auto-générée)

---

## ▶️ Lancer le projet

python main.py

---

## 🎮 Fonctionnalités

- Menu principal (Start / Charger / Quitter)
- Menu de paramétrage :
  - Température
  - Humidité
  - Nombre de prédateurs
  - Nombre de proies
- Simulation en temps réel
- Système de sauvegarde / chargement
- Menu pause avec modification des paramètres de génération suivante

---

## 🎮 Contrôles

| Action | Contrôle |
|---|---|
| Pause / Reprendre | Bouton PAUSE ou touche P / ESPACE |
| Accélérer la simulation | Bouton x1 / x2 / x5 / x10 |
| Relancer la simulation | Bouton RELANCER |
| Sauvegarder | Bouton SAUVER |
| Sélectionner un animal | Clic gauche |
| Afficher / cacher champ de vision | Touche V |
| Génération suivante manuelle | Touche N |
| Quitter | ÉCHAP |

---

## ⏸️ Menu Pause

Lorsque la simulation est en pause :

- Un menu overlay apparaît
- Permet de modifier :
  - Température future
  - Humidité future
  - Ajout de prédateurs
  - Ajout de proies

Ces paramètres seront appliqués à la prochaine génération.

---

## 🧠 Fonctionnement de la simulation

- Les plantes apparaissent selon les conditions environnementales
- Les proies :
  - Mangent les plantes
  - Évitent les prédateurs
- Les prédateurs :
  - Chassent les proies
- Les animaux possèdent :
  - Une vitesse
  - Une taille
  - Un champ de vision (FOV)

---

## 🔄 Générations

- Une génération se termine quand tous les animaux meurent
- Une nouvelle génération est créée automatiquement
- Les caractéristiques évoluent au fil du temps (sélection naturelle)

---

## 💾 Sauvegarde

Les simulations sont stockées dans une base SQLite (bdd.db).

Contenu sauvegardé :
- Nom de la simulation
- Génération
- Paramètres environnementaux
- Population

---

## 💡 Remarques

- Le projet utilise os.path → compatible Windows / Linux / macOS
- Interface entièrement développée avec pygame
- Architecture simple pour faciliter les modifications

---

## 👨‍💻 Auteurs

- BAZIZ Badis  
- GRAZIANI Olivier

---

## 🚀 Améliorations possibles

- Graphiques d’évolution
- IA plus avancée
- Carte avec obstacles
- Interface améliorée