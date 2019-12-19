# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 11:51:12 2019

@author: gaetan.galisot
"""

import FctModel
import VisuResult
import Donnee
import FctClustering
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


ClassDonnee = Donnee.CreationMultiProducteur(nb_prod, nb_clients_moy, perimetre, taux_clients, qte_moy, taux_qte, windows_moy, taux_windows, taux_remplissage, detour_max)


# Résolution du problème pour chaque producteurs
modMono = FctModel.ModelMonoProd(ClassDonnee)
optMono = modMono.modelCreationSolve()
print("optMono", optMono)


# Clustering des producteurs
init = FctClustering.ClusteringDistances(ClassDonnee, nb_clusters)
clusters_tab = np.zeros(nb_prod)
clusters_tab = init.ClusteringDistancesSolve()  # clusters_tab[p]=k ==> p est dans le cluster k


# affichage des clusters
print("clusters_tab : ", clusters_tab)


optMulti = np.zeros(nb_clusters) 
# Résolution pour chaque cluster
for cluster_num in range(0, nb_clusters):
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

print('Ratio = ', (np.sum(optMulti)/np.sum(optMono))-1)
