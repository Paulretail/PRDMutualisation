"""
Main permettant faire tourner l'heuristique plusieurs fois afin de simplifier les tests
"""
import copy
import sys
import FctModel
import Heuristique
import ParserDonnee
import read_JSON
import numpy as np

cas = 0
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
    if len(sys.argv) > 2:
        cas = int(sys.argv[2])
        if cas > 2:
            print(cas, " n'est pas un cas existant")
            sys.exit()
else:
    print("pas de fichier donné en paramètre")
    sys.exit()


# Résolution du problème pour chaque producteurs (sans mutualisation)
modMono = FctModel.ModelMonoProd(classe_donnee_buffer)
optMono, mono_chemin_buffer = modMono.modelCreationSolve()

resultat_total = 0
for i in range(100):
    classe_donnee = copy.deepcopy(classe_donnee_buffer)
    mono_chemin = copy.deepcopy(mono_chemin_buffer)

    # Résolution du problème sans cluster avec méthode aprochée
    heuristique = Heuristique.Heuristique(optMono, classe_donnee, mono_chemin)
    result_heuristique = heuristique.heuristique()
    print(np.around((1 - (np.sum(result_heuristique[1]) / np.sum(optMono)))*100,2))
    #print('Ratio = ', (1 - (np.sum(result_heuristique[1]) / np.sum(optMono))) * 100, "%")
    resultat_total = resultat_total + np.sum(result_heuristique[1])
print("Ratio moyen = ", (1 - ((resultat_total/100) / np.sum(optMono))) * 100, "%")
