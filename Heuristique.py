import random
import numpy as np


class Heuristique:

    def __init__(self, opt_mono, class_donnee, mono_chemin):
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

        # tableau à 2 dimension représentant le chemin parcouru par tous les producteurs
        # mono_chemin[0] permet d'accéder au chemin parcouru par le producteur 1 sous la forme d'une liste de point
        # chaque point est représenté par un tuple permettant de savoir à quel point il correspondait sur les données initiales
        self.chemin = mono_chemin

        # optimum pour chacun des producteurs sans cooperation, permet de calculer leur détour_max
        self.optMono = opt_mono

        # fonction objective à minimiser
        self.fonc_obj = np.sum(opt_mono)

        # tableau permettant de savoir combien de point d'un autre producteur sont dans ce chemin dim: nbProd * nbProd
        self.prod_dans_chemin = np.zeros((self.nb_prod, self.nb_prod))
        # instancie ce tableau
        for i in range(self.nb_prod):
            self.prod_dans_chemin[i][0] = self.nb_clients_p[i] - 1
        # TODO et un tableau faisant l'opposé dim : nbProd

    def heuristique_1(self):
        # choisit aléatoirement un producteur à qui on enlevera un client de son chemin
        rand_prod = random.randint(0, self.nb_prod - 1)

        # vérifie que le producteur ne soit pas seul sur son chemin
        while len(self.chemin[rand_prod]) <= 2:
            rand_prod = random.randint(0, self.nb_prod - 1)
        print(self.prod_dans_chemin)


    def heuristique_alea(self):
        # choisit aléatoirement un producteur à qui on enlevera un client de son chemin
        rand_prod = random.randint(0, self.nb_prod-1)

        # vérifie que le producteur ne soit pas seul sur son chemin
        while len(self.chemin[rand_prod]) <= 2:
            rand_prod = random.randint(0, self.nb_prod-1)

        # choisit un client aléatoire sur le chemin de ce producteur
        rand_client = random.randint(1, len(self.chemin[rand_prod])-2)

        # vérifie si le point enlevé est bien un client
        while self.chemin[rand_prod][rand_client][1] == 0:
            rand_prod = random.randint(0, self.nb_prod-1)
            rand_client = random.randint(1, len(self.chemin[rand_prod]) - 2)

        self.retirer_alea(rand_prod, rand_client)
        self.inserer_alea(rand_prod, rand_client)

    def retirer_alea(self, rand_prod, rand_client):
        # TODO si on enleve un client il faut vérifier si c'est le seul qui vient de son producteur et si c'est le cas il faut enlever son producteur et faire la mise à jour sur la fonction objective
        client_precedent = self.chemin[rand_prod-1][rand_client-1]
        client_suivant = self.chemin[rand_prod+1][rand_client+1]
        client = self.chemin[rand_prod][rand_client]

        # mise à jour de la fonction objective après avoir retiré le client
        self.fonc_obj = self.fonc_obj \
                        - self.dist[client[0], client[1], client_precedent[0], client_precedent[1]] \
                        - self.dist[client[0], client[1], client_suivant[0], client_suivant[1]] \
                        + self.dist[client_precedent[0], client_precedent[1], client_suivant[0], client_suivant[1]]

        self.chemin[rand_prod].pop(rand_client)

    def inserer_alea(self, rand_prod, rand_client):
        # TODO choisir un producteur aléatoire
        # TODO vérifier si le producteur du client à insérer est dans le chemin du producteur où on va inserer
        # TODO inserer le client à un endroit aléatoire (après son producteur si il est déjà dans le chemin) en respectant les contraintes
        # TODO si le producteur du client insérer n'est pas déjà dans ce chemin, l'insérer avant
        # TODO changer le poid à l'insertion du client puis à l'insertion du producteur
        print("b")





