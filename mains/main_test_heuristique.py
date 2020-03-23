"""
Main permettant faire tourner l'heuristique plusieurs fois afin se simplifier les tests
"""
import copy
import sys
import FctModel
import Heuristique
import ParserDonnee
import read_JSON
import numpy as np


# Si un fichier est donné en paramétre on le parse sinon on génére des données aléatoirement
if len(sys.argv) > 1:
    nom_fichier = str(sys.argv[1])
    if nom_fichier.split(".")[-1] == "xml":
        classe_donnee_buffer = ParserDonnee.parse(nom_fichier)
        nb_prod = classe_donnee_buffer.nb_prod
        nb_clusters = nb_prod // 2  # pour la fonction clustering
    elif nom_fichier.split(".")[-1] == "json":
        classe_donnee_buffer = read_JSON.read(nom_fichier)
        nb_prod = classe_donnee_buffer.nb_prod
        nb_clusters = nb_prod // 2  # pour la fonction clustering
else:
    print("no file given in parameter")
    sys.exit()

# Résolution du problème pour chaque producteurs (sans mutualisation)
modMono = FctModel.ModelMonoProd(classe_donnee_buffer)
optMono, mono_chemin_buffer = modMono.modelCreationSolve()
print("optMono", optMono)

for i in range(10):
    classe_donnee = copy.deepcopy(classe_donnee_buffer)
    mono_chemin = copy.deepcopy(mono_chemin_buffer)

    # Résolution du problème sans cluster avec méthode aprochée
    heuristique = Heuristique.Heuristique(optMono, classe_donnee, mono_chemin)
    result_heuristique = heuristique.heuristique()
    print('Ratio (cluster) = ', (1 - (np.sum(result_heuristique[1]) / np.sum(optMono))) * 100, "%")


