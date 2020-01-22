import numpy as np

import Donnee

import xml.etree.ElementTree as ET


def parse(nom_fichier):
    """parse le fichier donne en entree et retourne les donnees qu il contient dans l objet dataMultiProd"""
    tree = ET.parse(nom_fichier)
    root = tree.getroot()

    nb_prod = len(root.findall('producteur'))
    nb_clients_p = np.zeros(nb_prod, dtype=int)
    nb_clients_max = 0
    for i in range(0, nb_prod):     # trouve le nombre max de client
        nb_clients_p[i] = len(root.findall('producteur')[i].findall('client'))
        if nb_clients_p[i] > nb_clients_max:
            nb_clients_max = nb_clients_p[i]
    nb_clients_max = nb_clients_max + 1
    qte_p = np.zeros((nb_prod, nb_clients_max))
    windows_a_p = np.zeros((nb_prod, nb_clients_max))
    windows_b_p = np.zeros((nb_prod, nb_clients_max))
    s_loc_x_p = np.zeros((nb_prod, nb_clients_max))
    s_loc_y_p = np.zeros((nb_prod, nb_clients_max))
    capacite_p = np.zeros(nb_prod)

    detour_max = 0  # un seul detour_max

    # parcourt tous les producteurs
    i = 0
    for producteur in root.findall('producteur'):
        capacite_p[i] = float(producteur.find('capacite').text)
        s_loc_x_p[i][0] = float(producteur.find('locationxprod').text)
        s_loc_y_p[i][0] = float(producteur.find('locationyprod').text)
        detour_max = float(producteur.find('detourmax').text)
        # parcourt tous les clients
        j = 1
        for client in producteur.findall('client'):
            qte_p[i][j] = float(client.find('quantite').text)
            windows_a_p[i][j] = float(client.find('windowsa').text)
            windows_b_p[i][j] = float(client.find('windowsb').text)
            s_loc_x_p[i][j] = float(client.find('locationxclient').text)
            s_loc_y_p[i][j] = float(client.find('locationyclient').text)
            j += 1
        i += 1

    dist = Donnee.distance(s_loc_x_p, s_loc_y_p, nb_prod, nb_clients_max)

    class_donnee = Donnee.dataMultiProd(nb_prod, nb_clients_p, nb_clients_max, qte_p, windows_a_p, windows_b_p,
                                        s_loc_x_p, s_loc_y_p,
                                        capacite_p, dist, detour_max)
    return class_donnee
