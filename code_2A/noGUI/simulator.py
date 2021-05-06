import random as rd
import numpy as np
import time
import copy
import os
import pickle

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
        control, positions, nb_refPointBots = initialize_simulation(filename,width)
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

        angles_sim = np.linspace(0, 2*np.pi/nb_refPointBots, n_angle+1)
        angles_sim = angles_sim[:-1]

        print(len(positions_sim), len(angles_sim))

        # Création de toutes les combinaisons uniques de paramètres
        parameters = []
        for pos in positions_sim:
            for angle in angles_sim:
                parameters.append((pos,angle))

        print("\n")
        print("The simulator will now attempt to run %s simulations." %n_sim)
        input("Press Enter to start. ")

        dirname = os.path.dirname(__file__)
        simulation_number = 1
        file_number = 1
        multiple_metrics = {'sim_number'    : [],
                            'start_pos'     : [],
                            'start_angle'   : [],
                            'nbRefPointBots': [],
                            'nbMeasurerBots': [],
                            'algo_Measure'  : [],
                            'algo_RefPoint' : [],
                            'measuredTiles' : [],
                            'surface'       : [],
                            'pathLength'    : [],
                            'history'       : [],
                            'visitsPerTile' : [],
                            'sim_duration'  : []}

        ### Multiples simulations
        start = time.time()
        with click.progressbar(parameters) as bar:
            for params in bar:
                control_param = copy.deepcopy(control)
                metrics = launch_parametered_simulation(control_param,params)
                multiple_metrics['sim_number'].append(simulation_number)
                multiple_metrics['start_pos'].append(params[0])
                multiple_metrics['start_angle'].append(params[1])
                for key in metrics.keys():
                    multiple_metrics[key].append(metrics[key])


                simulation_number += 1
                if simulation_number % 20 == 0: # Toutes les 100 simulations, on sauvegarde les résultats dans un gros fichier.
                    file = open(os.path.join(dirname, "./results/",str(filename[8:-7])+"-noGUI-results-"+str(file_number)+".pickle"), "wb")
                    pickle.dump(metrics, file)
                    file.close()

                    multiple_metrics = {'sim_number'    : [],
                                        'start_pos'     : [],
                                        'start_angle'   : [],
                                        'nbRefPointBots': [],
                                        'nbMeasurerBots': [],
                                        'algo_Measure'  : [],
                                        'algo_RefPoint' : [],
                                        'measuredTiles' : [],
                                        'surface'       : [],
                                        'pathLength'    : [],
                                        'history'       : [],
                                        'visitsPerTile' : [],
                                        'sim_duration'  : []}
                    file_number += 1

        file = open(os.path.join(dirname, "./results/",str(filename[8:-7])+"-noGUI-results-"+str(file_number)+".pickle"), "wb")
        pickle.dump(metrics, file)
        file.close()

        print("Done in %3.2f seconds" %(time.time()-start))


if __name__ == '__main__':
    sim()