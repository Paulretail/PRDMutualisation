# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 13:18:24 2019

@author: gaetan.galisot
"""


import numpy as np

import math


def norm_l2(x1, y1, x2, y2):
    return math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))


class dataMonoProd:
    
    def __init__(self, nb_clients=0, qte=[], windows_a=[], windows_b=[], s_loc_x=[], s_loc_y=[], capacite=0):
        self.nb_clients = nb_clients    # nombre de clients
        self.qte = qte
        self.windows_a = windows_a
        self.windows_b = windows_b
        self.s_loc_x = s_loc_x
        self.s_loc_y = s_loc_y
        self.capacite = capacite
         
         
class dataMultiProd:
   
    def __init__(self, nb_prod=0, nb_clients_p=[], nb_clients_max=0, qte_p=[], windows_a_p=[], windows_b_p=[], s_loc_x_p=[], s_loc_y_p=[], capacite_p=[], dist=[], detour_max=0):
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
         
         
def CreationMultiProducteur(nb_prod, nb_clients_moy, perimetre, taux_clients, qte_moy, taux_qte, windows_moy, taux_windows, taux_remplissage, detour_max):
   
    nb_clients_p = np.zeros(nb_prod, dtype=int)
    nb_clients_max = int(nb_clients_moy*(1+taux_clients))+1  # pour la taille des tableaux
    s_loc_x_p = np.zeros((nb_prod, nb_clients_max))
    s_loc_y_p = np.zeros((nb_prod, nb_clients_max))
    qte_p = np.zeros((nb_prod, nb_clients_max))
    windows_a_p = np.zeros((nb_prod, nb_clients_max))
    windows_b_p = np.zeros((nb_prod, nb_clients_max))
    capacite_p = np.zeros(nb_prod)
    
    for p in range(0, nb_prod):
        nb_clients_p[p], qte_p[p], windows_a_p[p], windows_b_p[p], s_loc_x_p[p], s_loc_y_p[p], capacite_p[p] = CreationMonoProducteur(nb_clients_moy, nb_clients_max, perimetre, taux_clients, qte_moy, taux_qte, windows_moy, taux_windows, taux_remplissage)
    
    dist = distance(s_loc_x_p, s_loc_y_p, nb_prod, nb_clients_max)
    class_donnee = dataMultiProd(nb_prod=nb_prod, nb_clients_p=nb_clients_p, nb_clients_max=nb_clients_max, qte_p=qte_p, windows_a_p=windows_a_p, windows_b_p=windows_b_p, s_loc_x_p=s_loc_x_p, s_loc_y_p=s_loc_y_p, capacite_p=capacite_p, dist=dist, detour_max=detour_max)
    return class_donnee


def CreationMonoProducteur(nb_clients_moy, nb_clients_max, perimetre,taux_clients, qte_moy, taux_qte, windows_moy, taux_windows, taux_remplissage):
    # nb_clients_moy,perimetre,taux_clients, qte_moy, taux_qte, windows_moy, taux_windows, taux_remplissage
    # nb_clients \in [nb_clients-taux_clients, nb_clients+taux_clients]
    nb_clients = nb_clients_max  # nb_clients_max sert juste à donne une borne pour les tailles des vecteurs
    while nb_clients == nb_clients_max:
        nb_clients = nb_clients_moy*(1+taux_clients - 2*np.random.random()*taux_clients)
        nb_clients = math.floor(nb_clients)
        if nb_clients < 2:
            nb_clients = 2
            
    s_loc_x = np.zeros(nb_clients_max)
    s_loc_y = np.zeros(nb_clients_max)
    qte = np.zeros(nb_clients_max)
    windows_a = np.zeros(nb_clients_max)
    windows_b = np.zeros(nb_clients_max)
    # le producteur est situé dans un perimetre donné
    p_loc_x = np.random.random()*100
    p_loc_y = np.random.random()*100
    s_loc_x[0] = p_loc_x
    s_loc_y[0] = p_loc_y
      
    for j in range(1, nb_clients):
        # les client d'un producteur sont situés dans un perimetre du producteur
        s_loc_x[j] = p_loc_x + perimetre - 2*np.random.random()*perimetre
        s_loc_y[j] = p_loc_y + perimetre - 2*np.random.random()*perimetre
        # qte_p \in [qte_moy-taux_qte, qte_moy+taux_qte]
        qte[j] = qte_moy*(1+taux_qte - 2*np.random.random()*taux_qte)
        windows_a[j] = windows_moy*(1-taux_windows)
        windows_b[j] = windows_moy*(1+taux_windows)
    # capacite = capacite/taux_remplissage
    capacite = np.sum(qte) / taux_remplissage 
    return nb_clients, qte, windows_a, windows_b, s_loc_x, s_loc_y, capacite


def distance(s_loc_x_p, s_loc_y_p, nb_prod, nb_clients_max):
    # matrice sous forme [prod1, prod2, client_prod_1, client_prod2]
    matrice_dist = np.zeros((nb_prod, nb_clients_max, nb_prod, nb_clients_max))

    # on calcule les distances
    for p1 in range(0, len(s_loc_x_p[:, 0])):
        for s1 in range(0, len(s_loc_x_p[p1, :])):
            for p2 in range(0, len(s_loc_x_p[:, 0])):
                for s2 in range(0, len(s_loc_x_p[p2, :])):
                    matrice_dist[p1, s1, p2, s2] = norm_l2(s_loc_x_p[p1, s1], s_loc_y_p[p1, s1], s_loc_x_p[p2, s2], s_loc_y_p[p2, s2])
    return matrice_dist
