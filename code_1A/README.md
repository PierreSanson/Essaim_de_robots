Cette version du simulateur a pour but de donner une image très simplifiée du déplacement des robots lorsqu'ils sont collés les uns aux autres.
Le but est de pouvoir s'en servir pour vérifier le bon fonctionnement des algorithmes de formation de motifs.

Dans sa version actuelle, pour utiliser le simulateur il faut :

1) Lancer le fichier main.py
2) Cliquer sur "Choisir configuration initiale", ce qui ouvre une fenêtre.
3) Dans cette fenêtre, choisir la taille de la grille dans laquelle on va "dessiner" la configuration initiale de l'essaim, puis cliquer sur "afficher la grille".
4) On peut ensuite cocher les cases une à une, ou bien toutes d'un coup avec le bouton associé, puis cliquer sur le bouton "Valider et fermer cette fenêtre" pour enregistrer son choix. 
5) Répéter la même opération pour définir l'objectif, en cliquant cette fois sur "Choisir l'objectif".
6) Choisir le nombre d'itérations du programme.
7) Cliquer sur "Lancer la simulation", puis attendre que les calculs se fassent.
8) Une autre fenêtre avec une grille apparaît. CLiquer dessus puis utiliser les flèches gauche/droite du clavier pour faire défiler les déplacements des robots.

Pour l'instant, les robots ne bougent qu'un à la fois, en faisant le tour de l'essaim dans le sens des aiguilles d'une montre.
Si la configuration finale n'est pas la bonne, cela peut venir du fait que le nombre d'itérations est trop faible ou bien que notre algorithme est coincé (ce qui arrive souvent, dès que l'on donne des objectifs assez compacts et avec beaucoup de robots).
Les situations qui marchent bien sont pour l'instant les plus "linéaires", on alors avec de l'espace entre les embranchements, pour que les robots ne soient pas coincés.

MAJ nouvelle méthode de formation d'essaim:

La nouvelle méthode de formation d'essaim nommée "v2" par manque d'inspiration est plus rapide et fonctionne plus souvent que la méthode "clockwise".  
Elle utilise notamment le fait que chaque robot connait la dispostion de l'essaim à tout moment.  
Initialement, chaque robot calcul la longueur du chemin le plus court l'amenant à un point de la forme souhaitée, en faisant le tour de l'essaim actuel dans le sens horaire ou anti-horaire.  
Il propage alors cette information dans l'essaim de la même façon que la forme de l'essaim est propagée.  
Chaque Robot peut alors savoir si il a le chemin le plus court de l'essaim et si il doit alors bouger, ou bien si il doit rester en attente (en cas d'égalité, le robot possédant le plus grand numéro est prioritaire).  
Une fois que le robot ayant le plus court chemin a atteint la position visée, il propage cette information au reste de l'essaim.  
Le processus peut alors recommencer jusqu'à ce que la forme voulue soit obtenue. 