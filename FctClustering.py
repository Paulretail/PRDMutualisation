# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 09:29:16 2019

@author: chere
"""

import numpy as np
import random
from matplotlib import pyplot as plt
from sklearn.datasets.samples_generator import make_blobs
from sklearn.cluster import KMeans


def centreFct(nb_prod, s_loc_x_p, s_loc_y_p, nb_clients_p):
    # retourne un centre pour chaque producteur (egal à la moyenne des x de ses sites + dépot)
    centre_prod = np.zeros((nb_prod, 2))

    for p in range(0, nb_prod):
        centre_prod[p, 0] = np.mean(s_loc_x_p[p, 0:nb_clients_p[p]])
        centre_prod[p, 1] = np.mean(s_loc_y_p[p, 0:nb_clients_p[p]])

    return centre_prod


class ClusteringDistances:

    def __init__(self, class_donnee, nb_clusters):

        self.nb_prod = class_donnee.nb_prod
        self.nb_clients_p = class_donnee.nb_clients_p
        self.s_loc_x_p = class_donnee.s_loc_x_p
        self.s_loc_y_p = class_donnee.s_loc_y_p
        self.dist = class_donnee.dist
        self.nb_clusters = nb_clusters
          
    def ClusteringDistancesSolve(self):

        centre_prod = np.zeros((self.nb_prod, 2))
        centre_prod = centreFct(self.nb_prod, self.s_loc_x_p, self.s_loc_y_p, self.nb_clients_p)
        color = self.generate_colors(self.nb_prod)

        # affichage du centre pour chaque producteur
        for p in range(0, self.nb_prod):
            plt.scatter(self.s_loc_x_p[p, :1], self.s_loc_y_p[p, :1], marker='o', c=color[p])
            plt.scatter(self.s_loc_x_p[p, 1:self.nb_clients_p[p]+1], self.s_loc_y_p[p, 1:self.nb_clients_p[p]+1], marker='x', c=color[p])
            #plt.scatter(centre_prod[p, 0], centre_prod[p, 1], s=300, c='red', marker='8')

        plt.title('Centre de chaque producteur')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.show()
          
        # calcul du k-mean pour tt k
        wcss = []
        for i in range(1, self.nb_prod+1):
            kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
            kmeans.fit(centre_prod)
            wcss.append(kmeans.inertia_)

        plt.plot(range(1, self.nb_prod+1), wcss)
        plt.title('Elbow Method')
        plt.xlabel('# clusters')
        plt.ylabel('WCSS')
        plt.show()
          
        # on garde le k le plus interessant on suppose que c'est #prod/4 pour avoir en moyenne 3 producteurs par cluster
        print("nombre de cluster retenu = ", self.nb_clusters)
        kmeans = KMeans(n_clusters=self.nb_clusters, init='k-means++', max_iter=300, n_init=10, random_state=0)
        pred_y = kmeans.fit_predict(centre_prod)
        for p in range(0, self.nb_prod):
            plt.scatter(self.s_loc_x_p[p, :1], self.s_loc_y_p[p, :1], marker='x', c=color[p])
            plt.scatter(self.s_loc_x_p[p, 1:self.nb_clients_p[p]+1], self.s_loc_y_p[p, 1:self.nb_clients_p[p]+1], marker='o', c=color[p])
        plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=300, c='red', marker='8')
        plt.show()

        return kmeans.labels_

    def generate_colors(self, n):
        ret = []
        r = lambda: random.randint(0, 255)
        for i in range(n):
            color = '#%02X%02X%02X' % (r(), r(), r())
            ret.append(color)
        return ret
