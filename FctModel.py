# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 18:51:49 2019

@author: gaetan.galisot
"""

import numpy as np
import matplotlib.pyplot as plt
import math

from docplex.mp.model import Model


class ModelMonoProd:

    def __init__(self, class_donnee):

        self.nb_prod = class_donnee.nb_prod
        self.nb_clients_p = class_donnee.nb_clients_p
        self.nb_clients_max = class_donnee.nb_clients_max
        self.qte_p = class_donnee.qte_p
        self.windows_a_p = class_donnee.windows_a_p
        self.windows_b_p = class_donnee.windows_b_p
        self.s_loc_x_p = class_donnee.s_loc_x_p
        self.s_loc_y_p = class_donnee.s_loc_y_p
        self.capacite_p = class_donnee.capacite_p
        self.dist = class_donnee.dist

    def modelCreationSolve(self):
            
        M = 1000000

        # ------------- BEGIN: Create the mode ----------------------------------------
        opt = np.zeros(self.nb_prod)
        for p in range(0, self.nb_prod):
            # if np.sum(self.qte_p[p,:]) > self.capacite_p[p] :
                
            mdl = Model('4C')

            # Variables
            Xdimensions = [(i, j) for i in range(0, self.nb_clients_p[p]) for j in range(0, self.nb_clients_p[p])]
            x = mdl.integer_var_dict(Xdimensions, name="x")
            D = mdl.continuous_var_list(self.nb_clients_p[p], name='D')
            d_retour = mdl.continuous_var(name='d_f')

            # Objective function
            # mdl.minimize(mdl.sum(self.mat_tij[i][j] * x[i,j]  for i in self.S_all for j in self.S_all))
            mdl.minimize(d_retour - D[0])

            # Constraints

            mdl.add_constraints(mdl.sum(x[i, j] for i in range(0, self.nb_clients_p[p]) if i != j) == 1 for j in range(0, self.nb_clients_p[p]))

            mdl.add_constraints(mdl.sum(x[j, i] for i in range(0, self.nb_clients_p[p]) if i != j) == 1 for j in range(0, self.nb_clients_p[p]))

            mdl.add_constraints(D[j] >= D[i] + self.dist[p, i, p, j] - M * (1 - x[i, j]) for i in range(0, self.nb_clients_p[p]) for j in range(1, self.nb_clients_p[p]))

            mdl.add_constraints(D[j] >= self.windows_a_p[p, j] for j in range(0, self.nb_clients_p[p]))

            mdl.add_constraints(D[j] <= self.windows_b_p[p, j] for j in range(0, self.nb_clients_p[p]))

            mdl.add_constraints(d_retour >= D[i] + self.dist[p, i, p, 0] for i in range(0, self.nb_clients_p[p]))

            # mdl.print_information()
            solution = mdl.solve()
            opt[p] = solution.get_objective_value()
             
        return opt


class NotreModel:  

    def __init__(self, ClassDonnee, clusters_tab, cluster_num, optMono):

        # self.nb_prod = ClassDonnee.nb_prod
        # self.nb_clients_p = ClassDonnee.nb_clients_p
        # self.qte_p = ClassDonnee.qte_p
        # self.windows_a_p =ClassDonnee. windows_a_p
        # self.windows_b_p = ClassDonnee.windows_b_p
        # self.s_loc_x_p = ClassDonnee.s_loc_x_p
        # self.s_loc_y_p = ClassDonnee.s_loc_y_p
        # self.capacite_p = ClassDonnee.capacite_p
        # self.dist = ClassDonnee.dist
        # self.detour_max = ClassDonnee.detour_max
        # self.optMono = optMono

        clusters_tab_prod = np.where(np.in1d(clusters_tab, [cluster_num]))[0]
        self.nb_prod = len(clusters_tab_prod)
        self.nb_clients_p = ClassDonnee.nb_clients_p[clusters_tab_prod]
        self.qte_p = ClassDonnee.qte_p[clusters_tab_prod, :]
        self.windows_a_p = ClassDonnee. windows_a_p[clusters_tab_prod, :]
        self.windows_b_p = ClassDonnee.windows_b_p[clusters_tab_prod, :]

        self.s_loc_x_p = ClassDonnee.s_loc_x_p[clusters_tab_prod, :]

        self.s_loc_y_p = ClassDonnee.s_loc_y_p[clusters_tab_prod, :]
        self.capacite_p = ClassDonnee.capacite_p[clusters_tab_prod]

        self.dist = ClassDonnee.dist[clusters_tab_prod, :, :, :]
        self.dist = self.dist[:, :, clusters_tab_prod, :]

        self.detour_max = ClassDonnee.detour_max
        self.optMono = optMono[clusters_tab_prod]
        print("numProd -- nbClient")
        for p0 in range(0, self.nb_prod):
            print(p0, "--", self.nb_clients_p[p0])
     
    def modelCreation(self):
        """construit le problème"""

        M = 10000
        # ------------- BEGIN: Create the mode ----------------------------------------

        mdl = Model('4C')

        # Variables

        Xdimensions = [(p0, p1, s1, p2, s2) for p0 in range(0, self.nb_prod) for p1 in range(0, self.nb_prod) for s1 in range(0, self.nb_clients_p[p1]) for p2 in range(0, self.nb_prod) for s2 in range(0, self.nb_clients_p[p2])]
        x = mdl.integer_var_dict(Xdimensions, name="x")

        Ydimensions = [(p0, p1, s1)for p0 in range(0, self.nb_prod) for p1 in range(0, self.nb_prod) for s1 in range(0, self.nb_clients_p[p1])]
        y = mdl.binary_var_dict(Ydimensions, name="y")  # y_kk'j si k passe par j qui appartient à k'

        Ddimensions = [(p0, p1, s1)for p0 in range(0, self.nb_prod) for p1 in range(0, self.nb_prod) for s1 in range(0, self.nb_clients_p[p1])]
        D = mdl.continuous_var_dict(Ddimensions, name="D")
        R = mdl.continuous_var_list(self.nb_prod, name='R')  # date retour
        Tour = mdl.continuous_var_list(self.nb_prod, name='Tour')  # durée de tour (date départ - date d'arrivée)

        # Objective function

        mdl.minimize(mdl.sum(Tour[p0] for p0 in range(0, self.nb_prod)))

        # Constraints
        # AZ 1 consevation du flot
        for p0 in range(0, self.nb_prod):
            for p1 in range(0, self.nb_prod):
                for s1 in range(0, self.nb_clients_p[p1]):
                    mdl.add_constraint(mdl.sum(x[p0, p1, s1, p2, s2] for p2 in range(0, self.nb_prod) for s2 in range(0, self.nb_clients_p[p2]) if p1 != p2 or s1 != s2) == mdl.sum(x[p0, p2, s2, p1, s1] for p2 in range(0, self.nb_prod) for s2 in range(0, self.nb_clients_p[p2]) if p1 != p2 or s1 != s2))

        # AZ 2 tous les sites sont visités (p1,s1). cela signifie egalement que tous les producteurs sont visités car s1 commence à 0
        for p1 in range(0, self.nb_prod):
            for s1 in range(1, self.nb_clients_p[p1]):
                mdl.add_constraint(mdl.sum(y[p0, p1, s1] for p0 in range(0, self.nb_prod)) == 1)

        # AZ 3 Si un site s1 du producteur p1 est visité, alors le producteur p1 est visité (site 0)
        for p0 in range(0, self.nb_prod):
            for p1 in range(0, self.nb_prod):
                for s1 in range(1, self.nb_clients_p[p1]):
                    mdl.add_constraint(y[p0, p1, 0] >= y[p0, p1, s1])

        # AZ 4liaison entre les variables x et y. Si une tournée de p0 passe par (p1,s1) alors p0 visite (p1,s1)
        for p0 in range(0, self.nb_prod):
            for p1 in range(0, self.nb_prod):
                for s1 in range(0, self.nb_clients_p[p1]):
                    mdl.add_constraint(y[p0, p1, s1] == mdl.sum(x[p0, p1, s1, p2, s2] for p2 in range(0, self.nb_prod) for s2 in range(0, self.nb_clients_p[p2]) if p1 != p2 or s1 != s2))

        # AZ 5 on s'assure que la capacité des vehicules est respectée
        for p0 in range(0, self.nb_prod):
            mdl.add_constraint(mdl.sum(y[p0, p1, s1]*self.qte_p[p1, s1] for p1 in range(0, self.nb_prod) for s1 in range(1, self.nb_clients_p[p1])) <= self.capacite_p[p0])

        # AZ 6 retourne les dates d'arrivé aux sites
        for p0 in range(0, self.nb_prod):
            for p1 in range(0, self.nb_prod):
                for s1 in range(0, self.nb_clients_p[p1]):
                    for p2 in range(0, self.nb_prod):
                        for s2 in range(0, self.nb_clients_p[p2]):
                            if p2 != p0 or s2 != 0:
                                mdl.add_constraint(D[p0, p2, s2] >= D[p0, p1, s1] + self.dist[p1, s1, p2, s2] - M*(1 - x[p0, p1, s1, p2, s2]))

        # AZ 7 retourne la durée de la tournée pour chaque producteur
        #            for p0 in range(0,self.nb_prod):
        #                mdl.add_constraint(R[p0] ==  mdl.sum(self.dist[p1,s1,p2,s2] * x[p0,p1,s1,p2,s2] for p1 in range(0,self.nb_prod) for s1 in range(0,self.nb_clients_p[p1]) for p2 in range(0,self.nb_prod) for s2 in range(0,self.nb_clients_p[p2])))

        for p0 in range(0, self.nb_prod):
            for p2 in range(0, self.nb_prod):
                for s2 in range(0, self.nb_clients_p[p2]):
                    mdl.add_constraint(R[p0] >= D[p0, p2, s2] + self.dist[p2, s2, p0, 0] * x[p0, p2, s2, p0, 0])

        # AZ 8 respect des fenetres de temps
        for p0 in range(0, self.nb_prod):
            for p1 in range(0, self.nb_prod):
                for s1 in range(0, self.nb_clients_p[p1]):
                    if s1 != 0:
                        mdl.add_constraint(D[p0, p1, s1] >= self.windows_a_p[p1, s1]*y[p0, p1, s1])

        # AZ 9 respect des fenetres de temps
        for p0 in range(0, self.nb_prod):
            for p1 in range(0, self.nb_prod):
                for s1 in range(0, self.nb_clients_p[p1]):
                    if s1 != 0:
                        mdl.add_constraint(D[p0, p1, s1] <= self.windows_b_p[p1, s1]*y[p0, p1, s1])

        # AZ 10 Le producteur p0 passe chercher les produits d'un autre producteur p1 avant de les livrer ?
        for p0 in range(0, self.nb_prod):
            for p1 in range(0, self.nb_prod):
                for s1 in range(0, self.nb_clients_p[p1]):
                    if p1 != p0 and s1 != 0:
                        mdl.add_constraint(D[p0, p1, s1] >= D[p0, p1, 0])

        # AZ 11 La durée de la tournée de chaque producteur
        for p0 in range(0, self.nb_prod):
            mdl.add_constraint(Tour[p0] == R[p0]-D[p0, p0, 0])

        # AZ 12 Le détour max à ne pas depasser
        for p0 in range(0, self.nb_prod):
            mdl.add_constraint(Tour[p0] <= self.optMono[p0] * (1 + self.detour_max))

        # mdl.print_information()

        self.mdl = mdl

        return mdl

    def modelSolve(self, affiche=True):
        """résoud le problème avec une méthode exacte"""
        solution = self.mdl.solve()
        #            if affiche == True:
        #                print(self.mdl.solve_details)
        #                print(solution)
        return solution
