# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 11:51:12 2019
Main permettant de générer une instance de donnée aléatoire et d'en créer un fichier json
@author: chere
"""


import Donnee
import json

nb_prod = 10
nb_clients_moy = 5
perimetre = 50
taux_clients = 0
qte_moy = 10
taux_qte = 0.6
windows_moy = 300
taux_windows = 300
taux_remplissage = 0.5
detour_max = 0.7


ClassDonnee = Donnee.CreationMultiProducteur(nb_prod, nb_clients_moy, perimetre, taux_clients, qte_moy, taux_qte, windows_moy, taux_windows, taux_remplissage, detour_max)
data_dict = ClassDonnee.fctReturnDictCreationMultiProducteur()
with open("fichier_donnees_10prod.json", "w") as f:
    json.dump(data_dict, f, indent=5)
    


