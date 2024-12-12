# ETF_Analyzer

## Description

**ETF Analyzer** est un programme en C conçu pour analyser en temps réel les indices des ETF (Exchange Traded Funds) et les actualités financières associées. L'objectif est de fournir des analyses approfondies et des recommandations pour optimiser les placements financiers en fonction des tendances du marché et des informations pertinentes.

## Fonctionnalités Clés

- **Récupération de Données en Temps Réel :**
  - Collecte des données des indices ETF via des API financières.
  - Extraction des actualités financières pertinentes à partir de flux RSS ou d'API d'actualités.

- **Traitement et Préparation des Données :**
  - Nettoyage des données pour éliminer les anomalies.
  - Normalisation et mise en forme des données pour l'analyse.

- **Analyse via un Réseau de Neurones :**
  - Implémentation d'un réseau de neurones performant pour détecter des tendances et faire des prédictions.
  - Entraînement du modèle avec des données historiques pour améliorer la précision.

- **Corrélation avec les Actualités :**
  - Analyse de l'impact des actualités sur les mouvements des ETF.
  - Identification des corrélations significatives entre les événements et les fluctuations du marché.

- **Recommandations Stratégiques :**
  - Génération de recommandations pour réaligner les placements par secteur ou par place de marché.
  - Priorisation des opportunités d'investissement en fonction des analyses.

- **Interface Utilisateur Conviviale :**
  - Interface en ligne de commande permettant une interaction facile.
  - Personnalisation des paramètres d'analyse selon les préférences de l'utilisateur.

## Architecture du Projet

Le projet est structuré en plusieurs modules pour faciliter la maintenance et l'évolutivité :

- **src/** : Contient le code source du projet.
  - **data_acquisition/** : Récupération des données.
  - **data_processing/** : Traitement des données.
  - **neural_network/** : Système neuronal.
  - **analysis/** : Analyse et corrélation.
  - **recommendation/** : Génération de recommandations.
  - **ui/** : Interface utilisateur.
  - **utils/** : Fonctions utilitaires.
  - **models/** : Définitions des structures de données.

- **include/** : Fichiers d'en-tête (.h) pour chaque module.

- **tests/** : Tests unitaires et d'intégration pour assurer la qualité du code.

- **libs/** : Bibliothèques tierces utilisées dans le projet.

- **data/** : Données brutes et traitées.

- **configs/** : Fichiers de configuration.

- **build/** : Contient les fichiers compilés et l'exécutable.

## Installation et Compilation

**Prérequis :**

- Compilateur C compatible avec le standard C11.
- Bibliothèques externes nécessaires (par exemple, `libcurl`, `FANN`).

**Compilation :**

```bash
make
