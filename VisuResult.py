# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 12:32:11 2019

@author: gaetan.galisot
"""
import random

import matplotlib.pyplot as plt
import numpy as np


class visuPlot:
    """
    Classe permettant de visualiser les résultats (le chemin parcouru par chaque producteur) après la méthode exacte
    """

    def __init__(self, ClassDonnee, mdl, solution, clusters_tab, cluster_num):

        clusters_tab_prod = np.where(np.in1d(clusters_tab, [cluster_num]))[0]
        self.nb_prod = len(clusters_tab_prod)
        self.nb_clients_p = ClassDonnee.nb_clients_p[clusters_tab_prod]
        self.qte_p = ClassDonnee.qte_p[clusters_tab_prod, :]
        self.windows_a_p = ClassDonnee.windows_a_p[clusters_tab_prod, :]
        self.windows_b_p = ClassDonnee.windows_b_p[clusters_tab_prod, :]

        self.s_loc_x_p = ClassDonnee.s_loc_x_p[clusters_tab_prod, :]

        self.s_loc_y_p = ClassDonnee.s_loc_y_p[clusters_tab_prod, :]
        self.capacite_p = ClassDonnee.capacite_p[clusters_tab_prod]

        self.dist = ClassDonnee.dist[clusters_tab_prod, :, :, :]
        self.dist = self.dist[:, :, clusters_tab_prod, :]

        self.mdl = mdl
        self.solution = solution

    def afficheResult(self):
        """
        Affiche le chemin parcouru par chaque producteur grace à matplotlib
        """

        plt.figure()
        color = ['red', 'blue', 'green', 'black', 'yellow', 'purple', 'orange', 'grey']
        for p0 in range(0, self.nb_prod):
            plt.plot(self.s_loc_x_p[p0, 0], self.s_loc_y_p[p0, 0], color=color[p0], marker='o', linestyle='')
            for s1 in range(1, self.nb_clients_p[p0]):
                plt.plot(self.s_loc_x_p[p0, s1], self.s_loc_y_p[p0, s1], color=color[p0], marker='*',
                         linestyle='')  # sites de p0

        # affiche le numéro des points
        for p1 in range(0, self.nb_prod):
            for s1 in range(0, self.nb_clients_p[p1]):
                plt.annotate('$%d,%d$' % (p1, s1), (self.s_loc_x_p[p1, s1], self.s_loc_y_p[p1, s1]))

        # parse solution
        if self.mdl.solve_details.status_code == 101 or self.mdl.solve_details.status_code == 102:
            # print(solution.objective_value)
            sol_vars_ones = self.solution.as_dict()

            #                print(self.solution.get_value("D_1_1_1"))
            #                print(sol_vars_ones)

            for k, v in sol_vars_ones.items():
                # split based on _
                var_val = str(k).split("_")
                if var_val[0] == "x":  # treat th case of x variables
                    p0 = int(var_val[1])
                    p1 = int(var_val[2])
                    s1 = int(var_val[3])
                    p2 = int(var_val[4])
                    s2 = int(var_val[5])
                    plt.plot([self.s_loc_x_p[p1, s1], self.s_loc_x_p[p2, s2]],
                             [self.s_loc_y_p[p1, s1], self.s_loc_y_p[p2, s2]], color=color[p0])
            plt.show()
        else:
            print("MIP is not solved or infeasible")
            print(self.mdl.solve_details)


class VisuPlotHeuristique:
    """
    Classe permettant de visualiser les résultats (le chemin parcouru par chaque producteur) après l'heuristique
    """
    def __init__(self, class_donnee, chemin):

        self.nb_prod = class_donnee.nb_prod
        self.nb_clients_p = class_donnee.nb_clients_p
        self.qte_p = class_donnee.qte_p
        self.windows_a_p = class_donnee.windows_a_p
        self.windows_b_p = class_donnee.windows_b_p

        self.s_loc_x_p = class_donnee.s_loc_x_p

        self.s_loc_y_p = class_donnee.s_loc_y_p
        self.capacite_p = class_donnee.capacite_p

        self.dist = class_donnee.dist
        self.chemin = chemin

    def afficher_donnees(self):
        couleurs = self.generer_couleurs(self.nb_prod)

        # affichage du centre pour chaque producteur
        for p in range(0, self.nb_prod):
            plt.scatter(self.s_loc_x_p[p, :1], self.s_loc_y_p[p, :1], marker='o', c=couleurs[p])
            plt.scatter(self.s_loc_x_p[p, 1:self.nb_clients_p[p] + 1], self.s_loc_y_p[p, 1:self.nb_clients_p[p] + 1],
                        marker='x', c=couleurs[p])
        plt.title('Données')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.show()

    def afficher_result_heuristique(self):

        # TODO mettre ça dans une boucle comme dans le main
        plt.figure()
        couleurs = ['red', 'blue', 'green', 'black', 'yellow', 'purple', 'orange', 'grey']
        for p0 in range(self.nb_prod):
            plt.plot(self.s_loc_x_p[p0, 0], self.s_loc_y_p[p0, 0], color=couleurs[p0], marker='o', linestyle='')
            for s1 in range(1, len(self.chemin[p0]) - 1):
                plt.plot(self.s_loc_x_p[self.chemin[p0][s1][0], self.chemin[p0][s1][1]], self.s_loc_y_p[self.chemin[p0][s1][0], self.chemin[p0][s1][1]], color=couleurs[p0], marker='*', linestyle='')  # sites de p0

        plt.show()

    def generer_couleurs(self, n):
        """
        Génére des couleurs aléatoire pour pouvoir différencier chacun des producteurs

        :param n: int, nombre de couleurs à générer

        :return: tableau de string symbolisant les couleur en exadécimal
        """
        ret = []
        r = lambda: random.randint(0, 255)
        for i in range(n):
            color = '#%02X%02X%02X' % (r(), r(), r())
            ret.append(color)
        return ret