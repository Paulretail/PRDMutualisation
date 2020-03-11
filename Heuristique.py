import random
import numpy as np
import math
from operator import itemgetter
from FctClustering import centreFct


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

        # fonction objectif à minimiser
        self.fonc_obj = opt_mono.copy()

        # tableau permettant de savoir combien de point d'un autre producteur sont dans ce chemin dim: nbProd * nbProd
        self.prod_dans_chemin = np.zeros((self.nb_prod, self.nb_prod))
        # instancie ce tableau
        for i in range(self.nb_prod):
            self.prod_dans_chemin[i][i] = self.nb_clients_p[i] - 1
        # TODO et un tableau faisant l'opposé dim : nbProd

    def heuristique_1(self):
        # TODO répéter cela i fois
        #for _ in range(5):
        # choisit aléatoirement un producteur à qui on enlevera un client de son chemin
        rand_prod = random.randint(0, self.nb_prod - 1)

        # vérifie que le producteur ne soit pas seul sur son chemin
        while len(self.chemin[rand_prod]) <= 2:
            rand_prod = random.randint(0, self.nb_prod - 1)

        # selectionne un producteur par lequel le producteur precedent (rand_prod) passe
        # TODO peut etre amelioré
        rand_prod_change = random.randint(0, self.nb_prod - 1)
        while self.prod_dans_chemin[rand_prod][rand_prod_change] == 0:
            rand_prod_change = random.randint(0, self.nb_prod - 1)

        # nombre de point que l'on va retirer puis insérer
        # nb_change = random.randint(1, self.prod_dans_chemin[rand_prod][rand_prod_change])

        # liste tirée aléatoirement des index dans le chemin des clients qui vont être modifiés
        client_selectionne = random.sample(range(1, int(self.prod_dans_chemin[rand_prod][rand_prod_change]) + 1), int(self.prod_dans_chemin[rand_prod][rand_prod_change]))

        print("client_selectionne", client_selectionne)

        # liste des clients qui vont être modifiés
        client_change = [0 for i in range(int(self.prod_dans_chemin[rand_prod][rand_prod_change]))]

        # remplit client_change avec la liste des clients qui vont être modifiés
        position = -1
        for j in range(0, len(self.chemin[rand_prod])):
            if self.chemin[rand_prod][j][0] == rand_prod_change:
                position = position + 1
                try:
                    client_index = client_selectionne.index(position)
                    client_change[client_index] = self.chemin[rand_prod_change][j]
                except ValueError:
                    # ne fait rien
                    pass
        print("client_change", client_change)

        # trouve les producteurs les plus proche du producteur séléctionné aléatoirement
        list_prod = self.prod_voisin(rand_prod, math.floor(self.nb_prod/2))

        # en séléctionne un certain nombre aléatoirement dans cette liste
        list_prod_rand = random.sample(list_prod,  math.floor(self.nb_prod/3))

        meilleure_fonc_obj_p = 999999999
        meilleur_producteur = -1
        meilleur_nb_client_insert = -1
        meilleur_insert_position = []
        for p in list_prod_rand:
            fonc_obj_p = np.sum(self.fonc_obj)
            copie_chemin_p = self.chemin[p].copy()
            insert_position = []
            insert_position.append(-1)
            for n in range(len(client_change)):
                # effectue la meilleure insertion de client_change[n] dans le chemin copie_chemin_p
                resultat = self.meilleur_insert(rand_prod, rand_prod_change, client_change[n], copie_chemin_p)
                if len(resultat) > 2:
                    insert_position[0] = resultat[2]
                    fonc_obj_p = fonc_obj_p + resultat[1] + resultat[3]
                    insert_position.append(resultat[0])
                else:
                    fonc_obj_p = fonc_obj_p + resultat[1]
                    insert_position.append(resultat[0])
                if fonc_obj_p < meilleure_fonc_obj_p:
                    meilleure_fonc_obj_p = fonc_obj_p
                    meilleur_producteur = p
                    meilleur_nb_client_insert = n
                    meilleur_insert_position = insert_position
        print("chemin avant", self.chemin)
        print("client change", client_change)
        print("meilleur_nb_client_insert", meilleur_nb_client_insert + 1)
        print("meilleur_insert_position", meilleur_insert_position)
        print("meilleur_producteur", meilleur_producteur)
        print("0", self.fonc_obj)
        print("0", np.sum(self.fonc_obj))


        # On ajoute le premier point
        client = client_change[0]
        self.retirer_inserer_client(client, rand_prod, meilleur_producteur, meilleur_insert_position[1])

        # Après avoir ajouté le premier point on regarde si on a besoin d'ajouter le producteur
        if meilleur_insert_position[0] != -1:
            producteur = (rand_prod_change, 0)
            client_precedent_insert = self.chemin[meilleur_producteur][meilleur_insert_position[0]]
            client_suivant_insert = self.chemin[meilleur_producteur][meilleur_insert_position[0] + 1]

            # cout de l'insertion du producteur
            self.fonc_obj[meilleur_producteur] = self.fonc_obj[meilleur_producteur] + self.dist[producteur[0], producteur[1], client_precedent_insert[0], client_precedent_insert[1]] \
                            + self.dist[producteur[0], producteur[1], client_suivant_insert[0], client_suivant_insert[1]] \
                            - self.dist[client_precedent_insert[0], client_precedent_insert[1], client_suivant_insert[0], client_suivant_insert[1]]

            self.chemin[meilleur_producteur].insert(meilleur_insert_position[0]+1, producteur)

        # fait les meilleurs changements trouvés précédement
        for c in range(1, meilleur_nb_client_insert+1):

            client = client_change[c]
            self.retirer_inserer_client(client, rand_prod, meilleur_producteur, meilleur_insert_position[c+1])

        print("chemin apres", self.chemin)
        print("1", self.fonc_obj)
        print("1", np.sum(self.fonc_obj))
        # bonus faire des swap pour améliorer la solution

    def retirer_inserer_client(self, client, prod_retirer, prod_ajouter, position_insert):
        """ Retire puis insére le client

        Parameters
        ----------
        client : tupple, Le client que l'on va insérer

        prod_retirer : int, Le producteur auquel on va retirer des points de son chemin

        prod_ajouter : int, Le producteur auquel on va rajouter le client

        position_insert : int, La position où on va inserer le client
        """
        position_client = self.chemin[prod_retirer].index(client)
        client_precedent_retirer = self.chemin[prod_retirer][position_client - 1]
        client_suivant_retirer = self.chemin[prod_retirer][position_client + 1]

        # cout de retirer le client
        self.fonc_obj[prod_retirer] = self.fonc_obj[prod_retirer] - self.dist[client[0], client[1], client_precedent_retirer[0], client_precedent_retirer[1]] \
                                   - self.dist[client[0], client[1], client_suivant_retirer[0], client_suivant_retirer[1]] \
                                   + self.dist[client_precedent_retirer[0], client_precedent_retirer[1], client_suivant_retirer[0], client_suivant_retirer[1]]

        self.chemin[prod_retirer].remove(client)

        self.prod_dans_chemin[prod_retirer][client[0]] = self.prod_dans_chemin[prod_retirer][client[0]] - 1

        # si le client retiré est le dernier client appartenant au même producteur
        # alors il faut aussi retirer ce producteur de la liste
        if self.prod_dans_chemin[prod_retirer][client[0]] == 0 and client[0] != prod_retirer:
            producteur = (client[0], 0)
            position_prod = self.chemin[prod_retirer].index(producteur)
            client_precedent_retirer = self.chemin[prod_retirer][position_prod - 1]
            client_suivant_retirer = self.chemin[prod_retirer][position_prod + 1]

            # cout de retirer le producteur
            self.fonc_obj[prod_retirer] = self.fonc_obj[prod_retirer] - self.dist[producteur[0], producteur[1], client_precedent_retirer[0], client_precedent_retirer[1]] \
                                          - self.dist[producteur[0], producteur[1], client_suivant_retirer[0], client_suivant_retirer[1]] \
                                          + self.dist[client_precedent_retirer[0], client_precedent_retirer[1], client_suivant_retirer[0], client_suivant_retirer[1]]

            self.chemin[prod_retirer].remove(producteur)

        client_precedent_insert = self.chemin[prod_ajouter][position_insert]
        client_suivant_insert = self.chemin[prod_ajouter][position_insert + 1]

        # cout de l'insertion du client
        self.fonc_obj[prod_ajouter] = self.fonc_obj[prod_ajouter] \
                                      + self.dist[client[0], client[1], client_precedent_insert[0], client_precedent_insert[1]] \
                                      + self.dist[client[0], client[1], client_suivant_insert[0], client_suivant_insert[1]] \
                                      - self.dist[client_precedent_insert[0], client_precedent_insert[1], client_suivant_insert[0], client_suivant_insert[1]]

        self.chemin[prod_ajouter].insert(position_insert + 1, client)
        self.prod_dans_chemin[prod_ajouter][client[0]] = self.prod_dans_chemin[prod_ajouter][client[0]] + 1

    def meilleur_insert(self, prod_retirer, prod_change, client_change, copie_chemin_p):
        """ Insére client_change à sa meilleur mosition dans copie_chemin_p, insére aussi son producteur si nécessaire

        Parameters
        ----------
        prod_retirer : int, Le producteur auquel on va retirer des points de son chemin

        prod_change : int, Le producteur auquel appartenait les points modifiées originellement

        client_change : tupple, Le client que l'on veut insérer

        copie_chemin_p : list de tupple, Une copie du chemin parcouru par le producteur p
        """
        # tableau contenant l'index où client_change est inséré et le coût de cet insertion,
        # si son producteur est inséré resultat contiendra aussi ses informations
        resultat = []

        # si le producteur des points déplacés est déjà inséré dans le chemin du point p alors on commence à chercher après lui sinon on commence à 0
        try:
            position_prod = copie_chemin_p.index((prod_change, 0))
            insert_prod = False
        except ValueError:
            position_prod = 0
            insert_prod = True

        position_client_change = self.chemin[prod_retirer].index(client_change)

        client_precedent_retirer = self.chemin[prod_retirer][position_client_change-1]
        client_suivant_retirer = self.chemin[prod_retirer][position_client_change + 1]
        # TODO prendre en compte les contraintes
        # cout de retirer le client client_change du chemin du producteur prod_retirer
        cout_retirer = 0 - self.dist[client_change[0], client_change[1], client_precedent_retirer[0], client_precedent_retirer[1]] \
                       - self.dist[client_change[0], client_change[1], client_suivant_retirer[0], client_suivant_retirer[1]] \
                       + self.dist[client_precedent_retirer[0], client_precedent_retirer[1], client_suivant_retirer[0], client_suivant_retirer[1]]

        cout_best_insertion = 99999999
        meilleur_insert_position = -1
        for insert_position in range(position_prod, len(copie_chemin_p) - 1):
            client_precedent_insert = copie_chemin_p[insert_position]
            client_suivant_insert = copie_chemin_p[insert_position + 1]

            # cout de l'insertion du client à la position insert_position dans le chemin copie_chemin_p
            cout_insert = self.dist[client_change[0], client_change[1], client_precedent_insert[0], client_precedent_insert[1]] \
                          + self.dist[client_change[0], client_change[1], client_suivant_insert[0], client_suivant_insert[1]] \
                          - self.dist[client_precedent_insert[0], client_precedent_insert[1], client_suivant_insert[0], client_suivant_insert[1]]

            cout_change = cout_insert + cout_retirer

            if cout_best_insertion > cout_change:
                cout_best_insertion = cout_change
                meilleur_insert_position = insert_position

        resultat.append(meilleur_insert_position)
        resultat.append(cout_best_insertion)

        copie_chemin_p.insert(meilleur_insert_position+1, client_change)

        # si le producteur doit être inséré avant le client client_change alors on trouve sa meilleur position d'insertion ainssi que son coût
        if insert_prod:
            cout_best_insertion_prod = 9999999
            meilleur_insert_position_prod = -1
            producteur_change = (prod_change, 0)
            for insert_prod_position in range(0, meilleur_insert_position+1):
                client_precedent_insert = copie_chemin_p[insert_prod_position]
                client_suivant_insert = copie_chemin_p[insert_prod_position + 1]

                # cout de l'insertion du producteur à la position insert_prod_position dans le chemin copie_chemin_p
                cout_change_prod = self.dist[producteur_change[0], producteur_change[1], client_precedent_insert[0], client_precedent_insert[1]] \
                              + self.dist[producteur_change[0], producteur_change[1], client_suivant_insert[0], client_suivant_insert[1]] \
                              - self.dist[client_precedent_insert[0], client_precedent_insert[1], client_suivant_insert[0], client_suivant_insert[1]]

                if cout_best_insertion_prod > cout_change_prod:
                    cout_best_insertion_prod = cout_change_prod
                    meilleur_insert_position_prod = insert_prod_position
            copie_chemin_p.insert(meilleur_insert_position_prod+1, producteur_change)
            resultat.append(meilleur_insert_position_prod)
            resultat.append(cout_best_insertion_prod)

        return resultat

    def prod_voisin(self, prod, n):
        """ Retourne dans l'ordre les n producteurs les plus proches du producteur prod

        Parameters
        ----------
        prod : int, Le producteur dont on cherche les voisins

        n : int, Taille du voisinage recherché
        """
        # utilise la fonction centreFct pour trouver les centres de gravité des producteurs
        centre_prod = centreFct(self.nb_prod, self.s_loc_x_p, self.s_loc_y_p, self.nb_clients_p)

        # calcule la distance entre le centre gravité de prod et celui des autres producteurs
        distance = []
        for p in range(self.nb_prod):
            if p != prod:
                distance.append((p, math.sqrt(((centre_prod[p][0] - centre_prod[prod][0]) ** 2) + (
                        (centre_prod[p][1] - centre_prod[prod][1]) ** 2))))

        # trie la liste en fonction de son deuxième argument, donc les centres de gravités
        distance.sort(key=itemgetter(1))
        p_voisin = []
        for i in range(n):
            p_voisin.append(distance[i][0])
        return p_voisin

    def heuristique_alea(self):
        # choisit aléatoirement un producteur à qui on enlevera un client de son chemin
        rand_prod = random.randint(0, self.nb_prod - 1)

        # vérifie que le producteur ne soit pas seul sur son chemin
        while len(self.chemin[rand_prod]) <= 2:
            rand_prod = random.randint(0, self.nb_prod - 1)

        # choisit un client aléatoire sur le chemin de ce producteur
        rand_client = random.randint(1, len(self.chemin[rand_prod]) - 2)

        # vérifie si le point enlevé est bien un client
        while self.chemin[rand_prod][rand_client][1] == 0:
            rand_prod = random.randint(0, self.nb_prod - 1)
            rand_client = random.randint(1, len(self.chemin[rand_prod]) - 2)

        self.retirer_alea(rand_prod, rand_client)
        self.inserer_alea(rand_prod, rand_client)

    def retirer_alea(self, rand_prod, rand_client):
        # TODO si on enleve un client il faut vérifier si c'est le seul qui vient de son producteur et si c'est le cas il faut enlever son producteur et faire la mise à jour sur la fonction objective
        client_precedent = self.chemin[rand_prod - 1][rand_client - 1]
        client_suivant = self.chemin[rand_prod + 1][rand_client + 1]
        client = self.chemin[rand_prod][rand_client]

        # mise à jour de la fonction objectif après avoir retiré le client
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
        # TODO changer la fonction objetif à l'insertion du client puis à l'insertion du producteur
        print("b")
