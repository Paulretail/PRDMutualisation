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
    """
    Classe permettant de stocker toutes les données sur un producteur et ses clients
    """
    
    def __init__(self, nb_clients=0, qte=[], windows_a=[], windows_b=[], s_loc_x=[], s_loc_y=[], capacite=0):
        print("-----------------------------")
        self.nb_clients = nb_clients    # nombre de clients
        print("nb_clients : " + str(nb_clients))
        self.qte = qte
        print("qte : " + str(qte))
        self.windows_a = windows_a
        print("windows_a : " + str(windows_a))
        self.windows_b = windows_b
        print("windows_b : " + str(windows_b))
        self.s_loc_x = s_loc_x
        print("s_loc_x : " + str(s_loc_x))
        self.s_loc_y = s_loc_y
        print("s_loc_y : " + str(s_loc_y))
        self.capacite = capacite
        print("capacite : " + str(capacite))
        print("-----------------------------")
         
         
class dataMultiProd:
    """
    Classe permettant de stocker toutes les données sur les producteurs et leurs clients
    """
   
    def __init__(self, nb_prod=0, nb_clients_p=[], nb_clients_max=0, qte_p=[], windows_a_p=[], windows_b_p=[], s_loc_x_p=[], s_loc_y_p=[], capacite_p=[], dist=[], detour_max=0):
        self.nb_prod = nb_prod                  # nombre de producteurs
        self.nb_clients_p = nb_clients_p        # nombre de client par producteur
        self.nb_clients_max = nb_clients_max    # nombre de client possible au maximum
        self.qte_p = qte_p                      # matrice nbproducteur*nbclient, correspond a la quantite de produit vendu
        self.windows_a_p = windows_a_p          # matrice nbproducteur*nbclient, correspond au debut de sa fenetre de temps
        self.windows_b_p = windows_b_p          # matrice nbproducteur*nbclient, correspond a la fin de sa fenetre de temps
        self.s_loc_x_p = s_loc_x_p              # matrice nbproducteur*nbclient correspondant a la position en x de chacun des producteurs et clients
        self.s_loc_y_p = s_loc_y_p              # matrice nbproducteur*nbclient correspondant a la position en y de chacun des producteurs et clients
        self.capacite_p = capacite_p            # capacite de chacun des producteurs
        self.dist = dist                        # matrice des distances
        self.detour_max = detour_max            # detour maximum accepte, en pourcentage suplémentaire par rapport a sa solution idéale

    def fctReturnDictCreationMultiProducteur(self):
        """
        Transforme dataMultiProd en un dictionnaire.

        Cette fonction sert principalement pour écrire les données dans un fichier json

        :return: data_dict, un dictionnaire contenant tous les données de dataMultiProd
        """
        data_dict = {}
        producteur_list = []
        for p0 in range(0, self.nb_prod):

            producteur_dict = {}
            producteur_dict['id_producteur'] = p0
            producteur_dict['coordonnes'] = [self.s_loc_x_p[p0, 0], self.s_loc_y_p[p0, 0]]
            producteur_dict['capacite'] = self.capacite_p[p0]
            producteur_dict['fenetre_disponiblite'] = [self.windows_a_p[p0, 0], self.windows_b_p[p0, 0]]
            producteur_dict['detour_max'] = self.detour_max
            producteur_dict['nb_clients'] = int(self.nb_clients_p[p0])

            clients_list = []
            for s1 in range(1, self.nb_clients_p[p0]):
                clientsP0_dict = {}
                clientsP0_dict['id_client'] = [p0, s1]
                clientsP0_dict['coordonnes'] = [self.s_loc_x_p[p0, s1], self.s_loc_y_p[p0, s1]]
                clientsP0_dict['qte'] = self.qte_p[p0, s1]
                clientsP0_dict['fenetre_livraison'] = [self.windows_a_p[p0, s1], self.windows_b_p[p0, s1]]
                clients_list.append(clientsP0_dict)

            producteur_dict['clients'] = clients_list
            producteur_list.append(producteur_dict)

        data_dict['liste_producteurs'] = producteur_list
        data_dict['matrice_distances'] = self.dist.tolist()
        return data_dict


def CreationMultiProducteur(nb_prod, nb_clients_moy, perimetre, taux_clients, qte_moy, taux_qte, windows_moy, taux_windows, taux_remplissage, detour_max):
    """
    Lance la fonction CreationMonoProducteur pour créer plusieurs producteurs

    :param nb_prod: int, nombre de producteurs à créer

    :param nb_clients_moy: int, nombre de client moyen de ce producteur

    :param perimetre: int, distance max entre le producteur et ses clients

    :param taux_clients: float, taux de client que l'on désire

    :param qte_moy: float, quantité moyenne livrée

    :param taux_qte: float, taux de la quantité livrée

    :param windows_moy: float, moyenne permettant de définir la fenêtre de temps

    :param taux_windows:  float, taux permettant de définir la fenêtre de temps

    :param taux_remplissage: float, taux permettant de définir la capacité

    :param detour_max: float, pourcentage permettant de calculer le détour max des producteurs

    :return: une instance de la classe dataMultiProd contenant tous les producteurs et leurs clients générés
    """

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


def CreationMonoProducteur(nb_clients_moy, nb_clients_max, perimetre, taux_clients, qte_moy, taux_qte, windows_moy, taux_windows, taux_remplissage):
    """
    Créer un producteur aléatoirement

    :param nb_clients_moy: int, nombre de client moyen de ce producteur

    :param nb_clients_max: int, nombre de client max de ce producteur

    :param perimetre: int, distance max entre le producteur et ses clients

    :param taux_clients: float, taux de client que l'on désire

    :param qte_moy: float, quantité moyenne livrée

    :param taux_qte: float, taux de la quantité livrée

    :param windows_moy: float, moyenne permettant de définir la fenêtre de temps

    :param taux_windows:  float, taux permettant de définir la fenêtre de temps

    :param taux_remplissage:  float, taux permettant de définir la capacité

    :return: les données générées à partir des parametres
    """
    # nb_clients_moy,perimetre,taux_clients, qte_moy, taux_qte, windows_moy, taux_windows, taux_remplissage
    # nb_clients \in [nb_clients-taux_clients, nb_clients+taux_clients]
    nb_clients = nb_clients_max  # nb_clients_max sert juste à donne une borne pour les tailles des vecteurs
    while nb_clients == nb_clients_max:
        nb_clients = nb_clients_moy*(1+taux_clients - 2*np.random.random()*taux_clients)
        nb_clients = math.floor(nb_clients)
        if nb_clients < 2:
            nb_clients = 2
    print(nb_clients)
    print(nb_clients_max)
    print("-------------------------")
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
      
    for j in range(0, nb_clients):
        # les client d'un producteur sont situés dans un perimetre du producteur
        s_loc_x[j+1] = p_loc_x + perimetre - 2*np.random.random()*perimetre
        s_loc_y[j+1] = p_loc_y + perimetre - 2*np.random.random()*perimetre
        # qte_p \in [qte_moy-taux_qte, qte_moy+taux_qte]
        qte[j+1] = qte_moy*(1+taux_qte - 2*np.random.random()*taux_qte)
        windows_a[j+1] = windows_moy*(1-taux_windows)
        windows_b[j+1] = windows_moy*(1+taux_windows)
    # capacite = capacite/taux_remplissage
    capacite = np.sum(qte) / taux_remplissage 
    return nb_clients, qte, windows_a, windows_b, s_loc_x, s_loc_y, capacite


def distance(s_loc_x_p, s_loc_y_p, nb_prod, nb_clients_max):
    """
    Permet de calculer la matrice des distances

    :param s_loc_x_p: tableau de tableau de int, liste des coordonnées en x des clients et producteurs

    :param s_loc_y_p: tableau de tableau de int, liste des coordonnées en y des clients et producteurs

    :param nb_prod: int, nombre de producteurs

    :param nb_clients_max: int, nombre de client maximum possédé par un même producteur

    :return: la maatrice des distances sous la forme d'un tableau à 4 dim,
    dim 1 et 2 pour désigner le point avec son producteur et le l'id du client
    et dim 3 et 4 pour désigner de la même façon l'autre point
    """
    # matrice sous forme [prod1, prod2, client_prod_1, client_prod2]
    matrice_dist = np.zeros((nb_prod, nb_clients_max, nb_prod, nb_clients_max))

    # on calcule les distances
    for p1 in range(0, len(s_loc_x_p[:, 0])):
        for s1 in range(0, len(s_loc_x_p[p1, :])):
            for p2 in range(0, len(s_loc_x_p[:, 0])):
                for s2 in range(0, len(s_loc_x_p[p2, :])):
                    matrice_dist[p1, s1, p2, s2] = norm_l2(s_loc_x_p[p1, s1], s_loc_y_p[p1, s1], s_loc_x_p[p2, s2], s_loc_y_p[p2, s2])
    return matrice_dist
