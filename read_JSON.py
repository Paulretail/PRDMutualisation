# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 18:32:19 2020

@author: chere
"""

import numpy as np
import json


class dataMultiProd:

    def __init__(self, nb_prod=0, nb_clients_p=[], nb_clients_max=0, qte_p=[], windows_a_p=[], windows_b_p=[],
                 s_loc_x_p=[], s_loc_y_p=[], capacite_p=[], dist=[], detour_max=0):
        self.nb_prod = nb_prod
        self.nb_clients_p = nb_clients_p
        self.nb_clients_max = nb_clients_max
        self.qte_p = qte_p
        self.windows_a_p = windows_a_p
        self.windows_b_p = windows_b_p
        self.s_loc_x_p = s_loc_x_p
        self.s_loc_y_p = s_loc_y_p
        self.capacite_p = capacite_p
        self.dist = dist
        self.detour_max = detour_max


def read(adresse):
    with open(adresse) as json_data:
        data_dict = json.load(json_data)
        return jsonToClassDonnee(data_dict)


def jsonToClassDonnee(data):
    nb_prod = len(data['liste_producteurs'])
    nb_clients_p = np.zeros(nb_prod, dtype=int)

    for p0 in range(0, nb_prod):
        nb_clients_p[p0] = data['liste_producteurs'][p0]['nb_clients']

    nb_clients_max = max(nb_clients_p)
    s_loc_x_p = np.zeros((nb_prod, nb_clients_max))
    s_loc_y_p = np.zeros((nb_prod, nb_clients_max))
    qte_p = np.zeros((nb_prod, nb_clients_max))
    windows_a_p = np.zeros((nb_prod, nb_clients_max))
    windows_b_p = np.zeros((nb_prod, nb_clients_max))
    capacite_p = np.zeros(nb_prod)
    detour_max_p = np.zeros(nb_prod)

    for p0 in range(0, nb_prod):
        nb_clients_p[p0] = data['liste_producteurs'][p0]['nb_clients']
        capacite_p[p0] = data['liste_producteurs'][p0]['capacite']
        detour_max_p[p0] = data['liste_producteurs'][p0][
            'detour_max']  # je doit avoir le meme car detour_max est un float et non une liste dans la classe donnée
        s_loc_x_p[p0][0] = data['liste_producteurs'][p0]['coordonnes'][0]
        s_loc_y_p[p0][0] = data['liste_producteurs'][p0]['coordonnes'][1]
        windows_a_p[p0][0] = data['liste_producteurs'][p0]['fenetre_disponiblite'][0]
        windows_b_p[p0][0] = data['liste_producteurs'][p0]['fenetre_disponiblite'][1]

        for s1 in range(1, nb_clients_p[p0]):
            s_loc_x_p[p0][s1] = data['liste_producteurs'][p0]['clients'][s1 - 1]['coordonnes'][
                0]  # s1-1 car le producteur ne figure pas dans la liste de clients
            s_loc_y_p[p0][s1] = data['liste_producteurs'][p0]['clients'][s1 - 1]['coordonnes'][1]
            windows_a_p[p0][s1] = data['liste_producteurs'][p0]['clients'][s1 - 1]['fenetre_livraison'][0]
            windows_b_p[p0][s1] = data['liste_producteurs'][p0]['clients'][s1 - 1]['fenetre_livraison'][1]
            qte_p[p0][s1] = data['liste_producteurs'][p0]['clients'][s1 - 1]['qte']

    # dist = distance(s_loc_x_p,s_loc_y_p, nb_prod, nb_clients_max)
    dist = np.array(data['matrice_distances'])
    ClassDonnee = dataMultiProd(nb_prod=nb_prod, nb_clients_p=nb_clients_p, nb_clients_max=nb_clients_max, qte_p=qte_p,
                                windows_a_p=windows_a_p, windows_b_p=windows_b_p, s_loc_x_p=s_loc_x_p,
                                s_loc_y_p=s_loc_y_p, capacite_p=capacite_p, dist=dist, detour_max=detour_max_p[0])
    return ClassDonnee
