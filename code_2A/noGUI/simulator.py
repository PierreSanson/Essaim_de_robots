import random as rd
import numpy as np
import time

# Interface en ligne de commande pour le lancement de la simulation
import click

from drawing_to_simulation import load_and_launch_single_simulation, initialize_simulation, launch_parametered_simulation

@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('-w','--width', default=50, help='Specify the width of the tiles in the simulation.')
@click.option('--setup', is_flag=True, default=False, help='Use this option to trigger a series of prompts to setup a statistical test.')   

def sim(filename,width,setup):
    if not setup: # Lancement d'une seule simulation, emplacement initial du robot mesureur déterminé par le dessin de départ.
        duration = load_and_launch_single_simulation(filename,width)
        print("Done in %3.2f seconds" %duration)

    else: # Lancement de nombreuses simulations pour récolter des données statistiques.

        # Initialisation, pour créer la grille une seule fois.
        print("\n")
        print("Initializing the simulation...")
        control, positions = initialize_simulation(filename,width)
        print("Done\n")

        # Série de questions pour que l'utilisateur puisse rentrer ses paramètres.
        n_pos = len(positions)
        print("This simulation has %s available starting positions." %n_pos)
        try:
            n_pos_sim = int(input("How many positions do you want to simulate ? "))
        except ValueError:
            print("Not an integer - Aborting")
            return None

        if n_pos_sim > n_pos or n_pos < 1:
            print("Invalid number - Aborting")
            return None

        try:
            n_angle = int(input("How many starting angles would you like to test per starting position ? "))
        except ValueError:
            print("Not an integer - Aborting")
            return None

        if n_angle < 1:
            print("Invalid number - Aborting")
            return None

        # Calcul du nombre de simulations
        n_sim = n_pos_sim * n_angle

        # Calcul des différentes valeurs de positions initiales et angles initiaux
        if n_pos_sim < n_pos:
            rd.shuffle(positions)
            positions_sim = positions[:n_pos_sim]
        else :
            positions_sim = positions

        angles_sim = np.linspace(0, 2*np.pi, n_angle)

        print(len(positions_sim), len(angles_sim))

        # Création de toutes les combinaisons uniques de paramètres
        parameters = []
        for pos in positions_sim:
            for angle in angles_sim:
                parameters.append((pos,angle))
        print(len(parameters))
        print(parameters)

        print("\n")
        print("The simulator will now attempt to run %s simulations." %n_sim)
        input("Press Enter to start. ")
        
        ### Multiples simulations
        start = time.time()
        with click.progressbar(parameters) as bar:
            for params in bar:
                launch_parametered_simulation(control,params)
        print("Done in %3.2f seconds" %(time.time()-start))


if __name__ == '__main__':
    sim()