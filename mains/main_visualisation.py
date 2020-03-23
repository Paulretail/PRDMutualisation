"""
Main permettant de visualiser la solution pour un cas particulier et l'enregistre dans un fichier
"""
import sys

import FctModel
import VisuResult
import Donnee
import FctClustering
import ParserDonnee
import numpy as np
import Heuristique
import read_JSON

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

nb_clusters = nb_prod // 2  # pour la fonction clustering

# Si un fichier est donné en paramétre on le parse sinon on génére des données aléatoirement
if len(sys.argv) > 1:
    nom_fichier = str(sys.argv[1])
    if nom_fichier.split(".")[-1] == "xml":
        classe_donnee = ParserDonnee.parse(nom_fichier)
        nb_prod = classe_donnee.nb_prod
        nb_clusters = nb_prod // 2  # pour la fonction clustering
    elif nom_fichier.split(".")[-1] == "json":
        classe_donnee = read_JSON.read(nom_fichier)
        nb_prod = classe_donnee.nb_prod
        nb_clusters = nb_prod // 2  # pour la fonction clustering
else:
    classe_donnee = Donnee.CreationMultiProducteur(nb_prod, nb_clients_moy, perimetre, taux_clients, qte_moy, taux_qte,
                                                   windows_moy, taux_windows, taux_remplissage, detour_max)

'''print("nb_prod : " + str(classe_donnee.nb_prod))
print("nb_clients_p : " + str(classe_donnee.nb_clients_p))
print("nb_clients_max : " + str(classe_donnee.nb_clients_max))
print("qte_p : " + str(classe_donnee.qte_p))
print("windows_a_p : " + str(classe_donnee.windows_a_p))
print("windows_b_p : " + str(classe_donnee.windows_b_p))
print("s_loc_x_p : " + str(classe_donnee.s_loc_x_p))
print("s_loc_y_p : " + str(classe_donnee.s_loc_y_p))
print("capacite_p : " + str(classe_donnee.capacite_p))
#print("dist : " + str(classe_donnee.dist))
print("detour_max : " + str(classe_donnee.detour_max))'''

# Résolution du problème pour chaque producteurs (sans mutualisation)
modMono = FctModel.ModelMonoProd(classe_donnee)
optMono, mono_chemin = modMono.modelCreationSolve()
print("optMono", optMono)

# Résolution du problème sans cluster avec méthode aprochée
heuristique = Heuristique.Heuristique(optMono, classe_donnee, mono_chemin)
heuristique.heuristique()

# Affiche
Fenetre = VisuResult.VisuPlotHeuristique(classe_donnee, heuristique.chemin)
Fenetre.afficher_donnees()
Fenetre.afficher_result_heuristique()

# TODO afficher ça mais sans le centre des clusters

# Clustering des producteurs
init = FctClustering.ClusteringDistances(classe_donnee, nb_clusters)
clusters_tab = np.zeros(nb_prod)
clusters_tab = init.ClusteringDistancesSolve()  # clusters_tab[p]=k ==> p est dans le cluster k

# affichage des clusters
print("clusters_tab : ", clusters_tab)

optMulti = np.zeros(nb_clusters)
# Résolution pour chaque cluster


for cluster_num in range(0, nb_clusters):
    # Résolution avec méthode exacte
    mod = FctModel.NotreModel(classe_donnee, clusters_tab, cluster_num, optMono)
    mdl = mod.modelCreation()
    solution = mod.modelSolve()

    # affichage solution
    print('cluster : ', cluster_num, ' --> ', np.where(np.in1d(clusters_tab, [cluster_num]))[0])
    optMulti[cluster_num] = solution.get_objective_value()
    optMonoCluster = optMono[np.where(np.in1d(clusters_tab, [cluster_num]))[0]]
    print('objective = ', (solution.get_objective_value() / np.sum(optMonoCluster)) - 1)

    # Affiche
    Fenetre = VisuResult.visuPlot(classe_donnee, mdl, solution, clusters_tab, cluster_num)
    Fenetre.afficheResult()

print('optMono = ', optMono, ', sum optMono = ', np.sum(optMono))
print('optMulti = ', optMulti, ', sum optMulti = ', np.sum(optMulti))
print('Ratio = ', (1 - (np.sum(optMulti) / np.sum(optMono))) * 100, "%")
