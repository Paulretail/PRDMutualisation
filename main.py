# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 11:51:12 2019

@author: gaetan.galisot
"""
import sys

import FctModel
import VisuResult
import Donnee
import FctClustering
import ParserDonnee
import numpy as np


nb_prod = 10
nb_clients_moy = 3
perimetre = 50
taux_clients = 0.5
qte_moy = 10
taux_qte = 0.6
windows_moy = 300
taux_windows = 300
taux_remplissage = 0.6
detour_max = 0.7

nb_clusters = nb_prod//2  # pour la fonction clustering

if len(sys.argv) > 1:
    ClassDonnee = ParserDonnee.parse(str(sys.argv[1]))
    nb_prod = ClassDonnee.nb_prod
    nb_clusters = nb_prod // 2  # pour la fonction clustering
else:
    ClassDonnee = Donnee.CreationMultiProducteur(nb_prod, nb_clients_moy, perimetre, taux_clients, qte_moy, taux_qte, windows_moy, taux_windows, taux_remplissage, detour_max)

'''
print("nb_prod : " + str(ClassDonnee.nb_prod))
print("nb_clients_p : " + str(ClassDonnee.nb_clients_p))
print("nb_clients_max : " + str(ClassDonnee.nb_clients_max))
print("qte_p : " + str(ClassDonnee.qte_p))
print("windows_a_p : " + str(ClassDonnee.windows_a_p))
print("windows_b_p : " + str(ClassDonnee.windows_b_p))
print("s_loc_x_p : " + str(ClassDonnee.s_loc_x_p))
print("s_loc_y_p : " + str(ClassDonnee.s_loc_y_p))
print("capacite_p : " + str(ClassDonnee.capacite_p))
#print("dist : " + str(ClassDonnee.dist))
print("detour_max : " + str(ClassDonnee.detour_max))
'''

# Résolution du problème pour chaque producteurs (sans mutualisation)
modMono = FctModel.ModelMonoProd(ClassDonnee)
optMono = modMono.modelCreationSolve()
print("optMono", optMono)
# Résolution du problème sans cluster avec méthode exacte
# TODO

# Résolution du problème sans cluster avec méthode aprochée
# TODO

# Clustering des producteurs
init = FctClustering.ClusteringDistances(ClassDonnee, nb_clusters)
clusters_tab = np.zeros(nb_prod)
clusters_tab = init.ClusteringDistancesSolve()  # clusters_tab[p]=k ==> p est dans le cluster k

print("1")
# affichage des clusters
print("clusters_tab : ", clusters_tab)

optMulti = np.zeros(nb_clusters) 
# Résolution pour chaque cluster

print("1")
for cluster_num in range(0, nb_clusters):
    # Résolution avec méthode exacte
    mod = FctModel.NotreModel(ClassDonnee, clusters_tab, cluster_num, optMono)
    mdl = mod.modelCreation()
    solution = mod.modelSolve()
    
    # affichage solution
    print('cluster : ', cluster_num, ' --> ', np.where(np.in1d(clusters_tab, [cluster_num]))[0])
    optMulti[cluster_num] = solution.get_objective_value()
    optMonoCluster = optMono[np.where(np.in1d(clusters_tab, [cluster_num]))[0]]
    print('objective = ', (solution.get_objective_value()/np.sum(optMonoCluster))-1)
    
    # Affiche
    Fenetre = VisuResult.visuPlot(ClassDonnee, mdl, solution, clusters_tab, cluster_num)
    Fenetre.afficheResult()

    # Résolution avec méthode approchée
    # TODO

print('optMono = ', optMono, 'sum optMono = ', np.sum(optMono))
print('optMulti = ', optMulti, 'sum optMulti = ', np.sum(optMulti))
print('Ratio = ', (1-(np.sum(optMulti)/np.sum(optMono)))*100, "%")
