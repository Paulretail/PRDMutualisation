"""
Fichier comportant l'heuristique
"""

import random
import numpy as np
import math
from operator import itemgetter
from FctClustering import centreFct


class Heuristique:
    """
    Classe permettant d'utiliser l'heuristique
    """

    def __init__(self, opt_mono, class_donnee, mono_chemin):
        self.nb_prod = class_donnee.nb_prod
        self.nb_clients_p = class_donnee.nb_clients_p.copy()
        self.nb_clients_max = class_donnee.nb_clients_max.copy()
        self.qte_p = class_donnee.qte_p.copy()
        self.windows_a_p = class_donnee.windows_a_p.copy()
        self.windows_b_p = class_donnee.windows_b_p.copy()
        self.s_loc_x_p = class_donnee.s_loc_x_p.copy()
        self.s_loc_y_p = class_donnee.s_loc_y_p.copy()
        self.capacite_p = class_donnee.capacite_p.copy()
        self.dist = class_donnee.dist.copy()

        # tableau à 2 dimension représentant le chemin parcouru par tous les producteurs
        # mono_chemin[0] permet d'accéder au chemin parcouru par le producteur 1 sous la forme d'une liste de point
        # chaque point est représenté par un tuple permettant de savoir à quel point il correspondait sur les données initiales
        self.chemin = mono_chemin.copy()

        # tableau représentant la capacité restante sur ce chemin
        self.capacite_restant_p = []
        for i in range(self.nb_prod):
            self.capacite_restant_p.append(self.capacite_p[i] - sum(self.qte_p[i]))

        # distance max de chacun des producteurs, calculé à partir de leurs optimum sans cooperation et le detour_max
        self.detour_max = opt_mono * (1 + class_donnee.detour_max)

        # fonction objectif à minimiser
        self.fonc_obj = opt_mono.copy()

        # tableau permettant de savoir combien de point d'un autre producteur sont dans ce chemin dim: nbProd * nbProd
        self.prod_dans_chemin = np.zeros((self.nb_prod, self.nb_prod))
        # instancie ce tableau
        for i in range(self.nb_prod):
            self.prod_dans_chemin[i][i] = self.nb_clients_p[i] - 1
        # TODO et un tableau faisant l'opposé dim : nbProd

    def heuristique(self):
        """
        Fonction principale réalisant l'heuristique
        Elle choisit un producteur aléatoire, choisit des clients par leqeul passe ce producteur
        Puis en essaie d'enlever puis d'inserer ces clients dans des chemin d'autre producteur plus proche
        L'heuristique mémorise la meilleur insertion possible (vers quel producteur, combien de clients à insérer et où)
        et réalise cette insertion afin de créer une nouvelle solution
        On répéte ces étapes 500 fois, en mémorisant à chaque fois que l'on a une nouvelle meilleur solution

        :return: tupple contenant le chemin de la meilleur solution et son poids
        """
        fonc_obj_initial = np.sum(self.fonc_obj)
        fonc_obj_mono = np.sum(self.fonc_obj)
        best_sol = np.sum(self.fonc_obj)
        best_sols = self.fonc_obj.copy()
        compteur = 0
        best_iteration = -1
        best_chemin = self.chemin
        while compteur <= 500:
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
            # TODO changer les commentaires ici

            '''# Les deux premières livraisons d'un client sont considérée comme "urgente" et ne peuvent être réalisé que par lui-même
            if rand_prod == rand_prod_change:  # TODO justifier et corriger (cela provoque une erreur)
                print("eeeeeeeeeeeeeeeeeeeeeeeeee",int(self.prod_dans_chemin[rand_prod][rand_prod_change])-2)
                print("dzdz",self.nb_clients_p[rand_prod])

                # liste tirée aléatoirement des index dans le chemin des clients qui vont être modifiés
                client_selectionne = random.sample(range(3, int(self.prod_dans_chemin[rand_prod][rand_prod_change]) + 1), int(self.prod_dans_chemin[rand_prod][rand_prod_change])-2)
            else:
                # liste tirée aléatoirement des index dans le chemin des clients qui vont être modifiés
                client_selectionne = random.sample(range(1, int(self.prod_dans_chemin[rand_prod][rand_prod_change]) + 1), int(self.prod_dans_chemin[rand_prod][rand_prod_change]))
'''
            client_selectionne = random.sample(range(1, int(self.prod_dans_chemin[rand_prod][rand_prod_change]) + 1), int(self.prod_dans_chemin[rand_prod][rand_prod_change]))
            # liste des clients qui vont être modifiés
            client_change = [0 for _ in range(int(self.prod_dans_chemin[rand_prod][rand_prod_change]))]

            # remplit client_change avec la liste des clients qui vont être modifiés
            position = -1
            for j in range(0, len(self.chemin[rand_prod])):
                if self.chemin[rand_prod][j][0] == rand_prod_change:
                    position = position + 1
                    try:
                        client_index = client_selectionne.index(position)
                        client_change[client_index] = self.chemin[rand_prod][j]
                    except ValueError:
                        # ne fait rien
                        pass

            # trouve les producteurs les plus proche du producteur séléctionné aléatoirement
            list_prod = self.prod_voisin(rand_prod, math.floor(self.nb_prod/2))

            # en séléctionne un certain nombre aléatoirement dans cette liste
            list_prod_rand = random.sample(list_prod,  math.floor(self.nb_prod/3))
            # print("list_prod_rand",list_prod_rand)
            meilleure_fonc_obj_p = 999999999
            meilleur_producteur = -1
            meilleur_nb_client_insert = -1
            meilleur_insert_position = []
            for p in list_prod_rand:
                fonc_obj_p = np.sum(self.fonc_obj)
                copie_chemin_p = self.chemin[p].copy()
                copie_distance_p = self.fonc_obj[p]
                copie_capacite_restant_p = self.capacite_restant_p[p]
                insert_position = []
                # Si on n'a pas de producteur a inserer alors insert_position[0] vaut -1
                insert_position.append(-1)
                for n in range(len(client_change)):
                    # effectue la meilleure insertion de client_change[n] dans le chemin copie_chemin_p
                    resultat = self.meilleur_insert(rand_prod, rand_prod_change, client_change[n], copie_chemin_p, copie_distance_p, copie_capacite_restant_p)

                    # Test si l'insertion est valide
                    if resultat == 0:
                        # capacité max atteinte : on arrête
                        break
                    elif resultat == 1:
                        # detour max atteint : on arrête
                        break
                    elif len(resultat) > 4:
                        # On doit ajouter le producteur en plus du point
                        insert_position[0] = resultat[2]
                        fonc_obj_p = fonc_obj_p + resultat[1] + resultat[3]
                        copie_capacite_restant_p = resultat[4]
                        copie_distance_p = resultat[5]
                        insert_position.append(resultat[0])
                    else:
                        # On doit seulement le point
                        fonc_obj_p = fonc_obj_p + resultat[1]
                        copie_capacite_restant_p = resultat[2]
                        copie_distance_p = resultat[3]
                        insert_position.append(resultat[0])
                    if fonc_obj_p < meilleure_fonc_obj_p:
                        # si cette solution est meilleur, on la mémorise
                        meilleure_fonc_obj_p = fonc_obj_p
                        meilleur_producteur = p
                        meilleur_nb_client_insert = n
                        meilleur_insert_position = insert_position

            '''print("chemin avant", self.chemin)
            print("client change", client_change)
            print("meilleur_nb_client_insert", meilleur_nb_client_insert + 1)
            print("meilleur_insert_position", meilleur_insert_position)
            print("meilleur_producteur", meilleur_producteur)
            print("0", self.fonc_obj)'''
            # print("0", np.sum(self.fonc_obj))

            # si aucun point en peut être inséré car ne respectant pas les contraintes
            if len(meilleur_insert_position) < 1:
                continue

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

            '''print("chemin apres", self.chemin)
            print("1", self.fonc_obj)'''
            # print(compteur, "    ", np.sum(self.fonc_obj))

            if best_sol > np.sum(self.fonc_obj):
                # mémorise la meilleur solution
                best_sol = np.sum(self.fonc_obj)
                best_sols = self.fonc_obj.copy()
                best_chemin = self.chemin.copy()
                best_iteration = compteur
            fonc_obj_initial = np.sum(self.fonc_obj)
            compteur += 1
        '''print("compteur", compteur)
        print("fonc_obj_mono", fonc_obj_mono)
        print("best_sol", best_sol)
        print("ratio : ", (1 - (best_sol / fonc_obj_mono)) * 100, "%")
        print("best_iteration", best_iteration)
        print("best_chemin", best_chemin)'''
        # print("prod_dans_chemin", self.prod_dans_chemin)
        return best_chemin, best_sols

    def retirer_inserer_client(self, client, prod_retirer, prod_ajouter, position_insert):
        """
        Retire puis insére le client

        :param client: tupple, Le client que l'on va insérer

        :param prod_retirer: int, Le producteur auquel on va retirer des points de son chemin

        :param prod_ajouter: int, Le producteur auquel on va rajouter le client

        :param position_insert: int, La position où on va inserer le client
        """

        position_client = self.chemin[prod_retirer].index(client)
        client_precedent_retirer = self.chemin[prod_retirer][position_client - 1]
        client_suivant_retirer = self.chemin[prod_retirer][position_client + 1]

        # cout de retirer le client
        self.fonc_obj[prod_retirer] = self.fonc_obj[prod_retirer] \
                                      - self.dist[client[0], client[1], client_precedent_retirer[0], client_precedent_retirer[1]] \
                                      - self.dist[client[0], client[1], client_suivant_retirer[0], client_suivant_retirer[1]] \
                                      + self.dist[client_precedent_retirer[0], client_precedent_retirer[1], client_suivant_retirer[0], client_suivant_retirer[1]]

        self.chemin[prod_retirer].remove(client)
        self.prod_dans_chemin[prod_retirer][client[0]] = self.prod_dans_chemin[prod_retirer][client[0]] - 1

        # mise à jour de la capacité restante dans le chemin où on retire le client
        self.capacite_restant_p[prod_retirer] = self.capacite_restant_p[prod_retirer] + self.qte_p[client[0]][client[1]]

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

        # mise à jour de la capacité restante dans le chemin où on ajoute le client
        self.capacite_restant_p[prod_ajouter] = self.capacite_restant_p[prod_ajouter] - self.qte_p[client[0]][client[1]]

    def meilleur_insert(self, prod_retirer, prod_change, client_change, copie_chemin_p, copie_distance, copie_capacite_restant):
        """
        Insére client_change à sa meilleur position dans copie_chemin_p, insére aussi son producteur si nécessaire

        :param prod_retirer: int, Le producteur auquel on va retirer des points de son chemin

        :param prod_change: int, Le producteur auquel appartenait les points modifiées originellement

        :param client_change: tupple, Le client que l'on veut insérer

        :param copie_chemin_p: list de tupple, Une copie du chemin parcouru par le producteur p

        :param copie_distance: int, la distance parcourue dans le chemin copie_chemin_p

        :param copie_capacite_restant: int, la capacite restante du producteur parcourant le chemin copie_chemin_p

        :return: resultat, array, tableau contenant l'index où client_change est inséré et le coût de cet insertion, si son producteur est inséré resultat contiendra aussi ses informations
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

        # cout de retirer le client client_change du chemin du producteur prod_retirer
        cout_retirer = 0 - self.dist[client_change[0], client_change[1], client_precedent_retirer[0], client_precedent_retirer[1]] \
                       - self.dist[client_change[0], client_change[1], client_suivant_retirer[0], client_suivant_retirer[1]] \
                       + self.dist[client_precedent_retirer[0], client_precedent_retirer[1], client_suivant_retirer[0], client_suivant_retirer[1]]

        cout_best_insertion = 99999999
        meilleur_insert_position = -1
        cout_distance_plus = 0
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
                cout_distance_plus = cout_insert
                meilleur_insert_position = insert_position

        resultat.append(meilleur_insert_position)
        resultat.append(cout_best_insertion)

        copie_chemin_p.insert(meilleur_insert_position+1, client_change)

        # si le producteur doit être inséré avant le client client_change alors on trouve sa meilleur position d'insertion ainssi que son coût
        cout_distance_plus_prod = 0
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
                    cout_distance_plus_prod = cout_best_insertion_prod
                    meilleur_insert_position_prod = insert_prod_position
            copie_chemin_p.insert(meilleur_insert_position_prod+1, producteur_change)
            resultat.append(meilleur_insert_position_prod)
            resultat.append(cout_best_insertion_prod)

        # si la contrainte de poids n'est plus respectée alors on arrete
        if (copie_capacite_restant - self.qte_p[client_change[0]][client_change[1]]) < 0:
            return 0
        else:
            resultat.append(copie_capacite_restant - self.qte_p[client_change[0]][client_change[1]])

        # si la contrainte de detour max n'est plus respectée alors on arrete
        if cout_distance_plus_prod + cout_distance_plus + copie_distance > self.detour_max[copie_chemin_p[0][0]]:
            return 1
        else:
            resultat.append(cout_distance_plus_prod + cout_distance_plus + copie_distance)

        return resultat

    def prod_voisin(self, prod, n):
        """
        Retourne dans l'ordre les n producteurs les plus proches du producteur prod

        :param prod: int, Le producteur dont on cherche les voisins

        :param n: int, Taille du voisinage recherché

        :return: p_voisin, array de int, les n producteurs les plus proches du producteur prod (dans l'ordre)
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
