# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 14:01:10 2026

@author: saint-genesj
"""

import os

base_dir = "."

problemes = []

for dossier_tx in os.listdir(base_dir):
    # garder seulement les TXxD
    if not dossier_tx.startswith("TX") or not dossier_tx.endswith("D"):
        continue

    chemin_tx = os.path.join(base_dir, dossier_tx)

    if not os.path.isdir(chemin_tx):
        continue

    for nom in os.listdir(chemin_tx):
        chemin_nom = os.path.join(chemin_tx, nom)

        if not os.path.isdir(chemin_nom):
            continue

        # compter les fichiers .nc
        fichiers = [f for f in os.listdir(chemin_nom) if f.endswith(".nc")]
        nb = len(fichiers)

        if nb != 3:
            problemes.append((dossier_tx, nom, nb))

# Affichage des problèmes
if not problemes:
    print("✅ Tout est OK : 3 fichiers partout")
else:
    print("❌ Problèmes détectés :\n")
    for tx, nom, nb in problemes:
        print(f"{tx}/{nom} → {nb} fichiers")