# SCADEN — Simulation de Chaîne Alimentaire Dans un Environnement Naturel

---

## 1. Présentation globale du projet

### Naissance de l'idée

Tout a commencé quand Badis a découvert les Trophées NSI. Après avoir consulté le thème de l'année 2025-2026, il m'a proposé de le rejoindre. J'ai tout de suite accepté, même si nous ne savions pas encore quel projet réaliser. Un soir, nous nous sommes appelés pour brainstormer et l'idée de SCADEN est née progressivement. Au départ, nous étions partis sur un projet de gestion de forêt, puis nous avons réfléchi aux animaux que nous pourrions y intégrer. Finalement, le concept a évolué pour passer d'une simple gestion forestière à un système de sélection naturelle.

### Problématique initiale

Comment simuler informatiquement l'évolution d'un écosystème composé de plantes, de proies et de prédateurs, soumis à des contraintes environnementales variables, et observer l'émergence de comportements et d'adaptations au fil des générations ?

### Objectifs

- Modéliser un écosystème avec trois niveaux trophiques : plantes, proies et prédateurs.
- Implémenter un moteur physique 2D gérant les déplacements, les collisions et les zones de détection.
- Simuler l'influence de l'environnement (température, humidité) sur la végétation et les comportements.
- Appliquer un algorithme de sélection naturelle pour faire évoluer les caractéristiques des animaux (vitesse, taille, champ de vision) au fil des générations.
- Proposer une interface graphique interactive permettant de paramétrer et d'observer la simulation en temps réel.

---

## 2. Organisation du travail

### Présentation de l'équipe

| Prénom Nom | Niveau | Rôle principal |

| Baziz Badis | Terminale | Partie moteur physique, environnement, animaux, déplacements, détections, collisions|
| Graziani Olivier | Terminale | Partie interface graphique, base de données |

### Temps passé sur le projet

Un mois a été dédié à ce projet ; après les cours, du temps a été passé sur ce projet par chacun d'entre nous.
---

## 3. Présentation des étapes du projet

### Étape 1 — Conception de l'architecture (début mars 2026)

Définition de la structure du projet en modules distincts : moteur physique et classes des créatures, environnement, interface graphique et base de données. Mise en place du dépôt Git et de l'environnement de développement.

### Étape 2 — Moteur physique et déplacements (8-10 mars)

Implémentation des déplacements 2D avec gestion des collisions aux bords de l'écran. Ajout du bruit de Perlin pour simuler une errance naturelle et réaliste des animaux.

### Étape 3 — Classes des créatures (9-11 mars)

Création de la hiérarchie de classes `Animaux → Predateur / Proie` et de la classe `Plante`. Chaque animal possède des attributs génétiques (vitesse, taille, champ de vision) et un système d'énergie. La proie fuit les prédateurs et mange les plantes ; le prédateur chasse les proies.

### Étape 4 — Environnement et sélection naturelle (11-13 mars)

Développement de la classe `Monde` qui gère la température, l'humidité et la pousse des plantes en fonction des conditions climatiques. Implémentation de l'algorithme de sélection : les animaux ayant fait les meilleures performances survivent et se reproduisent en donnant à leurs enfants certaines de leurs caractéristiques, avec une légère mutation (modifiable dans le programme par l'utilisateur).

### Étape 5 — Interface graphique et menus (14-20 mars)

Création du menu principal, du menu de paramétrage (sliders température/humidité, saisie du nom de simulation) et de la boucle de simulation. L'interface affiche en temps réel les statistiques, le numéro de génération, et permet de sélectionner un animal pour consulter ses attributs.

### Étape 6 — Base de données et sauvegarde (15 mars)

Intégration de SQLite pour sauvegarder les noms de simulation et les statistiques de chaque génération (nombre de prédateurs/proies, vitesse du meilleur individu).

### Étape 7 — Tests, corrections et documentation (20-27 mars)

Correction des bugs (freeze de l'affichage, gestion de la fenêtre, logique des boutons), optimisation de la boucle de simulation, rédaction de la documentation.

---

## 4. Validation de l'opérationnalité du projet

### État d'avancement au moment du dépôt

Le projet est fonctionnel dans son intégralité :
- La simulation tourne à 60 FPS avec gestion correcte des générations.
- L'algorithme de sélection produit une évolution visible des attributs au fil des générations jusqu'à une stratégie optimale pour les prédateurs ou les proies, ou un équilibre.
- L'interface permet de paramétrer, observer, mettre en pause, accélérer et sauvegarder la simulation.

### Approches mises en œuvre pour vérifier le fonctionnement

- Tests manuels de chaque fonctionnalité à chaque étape de développement.
- Vérification de la cohérence de l'algorithme de sélection en affichant les attributs du meilleur individu dans la console à chaque génération.
- Tests avec des valeurs extrêmes de température et d'humidité (0 et 100) pour vérifier la robustesse de la génération des plantes.

### Difficultés rencontrées et solutions apportées

| Difficulté | Solution apportée |
|---|---|
| La fenêtre pygame freezait lors du lancement de la simulation | L'écran était créé en 800×600 dans `settings.py` mais la simulation nécessitait 1000×800 ; résolution en redimensionnant dynamiquement la fenêtre dans `simulation_loop()` |
| Le bouton Pause ne fonctionnait pas | Utilisation de `pygame.mouse.get_pressed()` au lieu de `MOUSEBUTTONDOWN` : le toggle s'activait 60 fois par frame et se neutralisait ; corrigé en centralisant tous les clics dans la boucle d'événements |
| Les textes du panneau de stats s'affichaient hors écran | La fonction `dessiner_texte` de `settings.py` utilisait l'écran global 800×600 ; création d'une fonction locale `dessiner_texte_local(surface, ...)` prenant la surface en paramètre |
| Les créatures avaient un mouvement trop peu réaliste et très saccadé | Intégration du bruit de perlin pour des mouvements naturels |

---

## 5. Ouverture

### Idées d'amélioration

- **Graphiques d'évolution** : afficher en temps réel des courbes du nombre d'individus et de l'évolution des attributs génétiques par génération.
- **Réseau Neuronal** : utiliser un réseau de neurone et des algorithmes de machine learning pour voir émerger des stratégies inattendues.
- **Météo dynamique** : faire varier la température et l'humidité au cours de la simulation pour créer des événements climatiques.
- **Reproduction sexuée** : croiser deux parents au lieu de muter un seul individu, pour un algorithme génétique plus réaliste.
- **Décors adaptatifs** : modifier l'apparence visuelle de la zone de simulation en fonction des paramètres environnementaux.
- **Export des données** : générer des fichiers CSV ou des graphiques matplotlib pour analyser les résultats après simulation.

### Analyse critique

Le projet remplit ses objectifs principaux. L'algorithme de sélection est fonctionnel et produit une évolution observable. Cependant, l'utilisation de pygame, bien que pratique pour l'affichage, présente des contraintes de portabilité signalées par le règlement du concours. Une version future pourrait envisager une interface web ou une visualisation via matplotlib pour s'affranchir de cette dépendance.
Malgré le fait qu'on puisse observer une adaptation en temps réel et des résultats intéréssants, les simulations aboutissent souvent à des résultats prévisibles.

### Compétences personnelles développées

- Programmation orientée objet avancée (héritage, polymorphisme).
- Algorithmique : algorithme de sélection naturelle, bruit de Perlin, calculs vectoriels 2D.
- Gestion d'une base de données SQLite depuis Python.
- Développement d'une interface graphique événementielle avec pygame.
- Travail collaboratif avec Git.
- Répartition des taches équitables et coordination.
- Gestion du temps et planification.