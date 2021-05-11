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
@click.argument('path', type=click.Path(exists=True))
@click.option('-w','--width', default=50, help='Specify the width of the tiles in the simulation.')
@click.option('-r','--recursive', is_flag=True, default=False)
@click.option('--setup', is_flag=True, default=False, help='Use this option to trigger a series of prompts to setup a statistical test.')   

def sim(path,width,recursive,setup):

    if not setup: # Lancement d'une seule simulation, emplacement initial du robot mesureur déterminé par le dessin de départ.
        if recursive:
            print("You cannot run a single simulation on a folder !")
            return None

        duration = load_and_launch_single_simulation(path,width)
        print("Done in %3.2f seconds" %duration)


    else: # Lancement de nombreuses simulations pour récolter des données statistiques.
        answers = get_answers()

        if recursive:
            list_control = []
            list_params = []
            list_filename = []

            print("There are %s rooms in the selected folder." %len(os.listdir(path)))
            print("\n")
            print("Initializing the simulations...")

            for filename in os.listdir(path):
                control = init_sim(os.path.join(path,filename),width,recursive)
                control, params = setup_sim(control,answers,recursive)
                list_control.append(control)
                list_params.append(params)
                list_filename.append(os.path.join(path,filename))
            
            n_sim = 0
            for params in list_params:
                n_sim += len(params)

            print("Done")

            print("\n")
            print("The simulator will now attempt to run %s simulations." %n_sim)
            input("Press Enter to start. ")

            for k in range(len(list_control)):
                multi_sim(list_control[k],list_params[k],list_filename[k])    
            
        else:
            filename = path
            control = init_sim(filename,width,recursive)
            control, params = setup_sim(control,answers,recursive)
            multi_sim(control,params,filename)


def init_sim(filename,width,recursive):
        # Initialisation, pour créer la grille une seule fois.
        if not recursive :
            print("\n")
            print("Initializing the simulation...")
            control = initialize_simulation(filename,width)
            print("Done\n")
        else :
            control = initialize_simulation(filename,width)

        return control


def get_answers():
    try:
        print("\n")
        answer_h = str(input("Do you want to save a detailed historic of the state of each tile ? [y/n] "))
    except ValueError:
        print("Invalid entry - Aborting")
        return None
    print("\n")
    
    if answer_h not in ['y','n']:
        print('Please answer with yes [y] or no [n] - Aborting')
        return None
        
    # Nombre de positions de départ
    try:
        n_pos_percent = int(input("What percentage of starting positions would you like to test ? "))
    except ValueError:
        print("Not an integer - Aborting")
        return None

    if  n_pos_percent < 0 or n_pos_percent > 100:
        print("Invalid number - Aborting")
        return None
    
    # Nombres d'angles de départ par postion de départ
    try:
        n_angle = int(input("How many starting angles would you like to test per starting position ? "))
    except ValueError:
        print("Not an integer - Aborting")
        return None

    if n_angle < 1:
        print("Invalid number - Aborting")
        return None

    # Nombre de robots points de repère
    try:
        print("\nHow many RefPointBots ?")
        n_rp_bots_min = int(input("From : "))
        n_rp_bots_max = int(input("To : "))
    except ValueError:
        print("Not an integer - Aborting")
        return None

    if n_rp_bots_min < 1 or n_rp_bots_max < n_rp_bots_min:
        print("Invalid number - Aborting")
        return None

    # Types de méthodes :
    try:
        print("\nYou will now select the different methods that need to be tested.\r")
        print("If you want to select multiple methods in each category, simply type more than one number.\n")

        target_method = str(input("Target Methods : 1='findTargetV1' 2='findTargerV2' 3='findTargetV3' "))
        cluster_exploration_method = str(input("Cluster Exploartion Methods : 1='findClosestClusterToOrigin' 2='findClosestClusterToMeasurerBot' "))
        visited_cluster_exploration_method = str(input("Visited Cluster Exploartion Methods: same choices "))
        RPB_selection_method = str(input("Target Methods : 1='findLeastUsefulBots' 2='findLeastUsefulBotsV2' "))
        change_first = str(input("Cahnge First : 1='cluster' 2='RPB' "))
        anti_loop_method = str(input("Anti Loop Method : 1='agressive' 2='patient' "))

    except ValueError:
        print("Value Error - Aborting")
        return None

    # conversion des entrées de l'utilisateur
    tmp = []
    for char in target_method:
            if char in ["1","2","3"]:
                tmp.append(int(char))
            elif char != " ":
                print("Not a valid number - Aborting")
                return None
    target_method = tmp

    tmp = []
    for char in cluster_exploration_method:
            if char in ["1","2"]:
                tmp.append(int(char))
            elif char != " ":
                print("Not a valid number - Aborting")
                return None
    cluster_exploration_method = tmp

    tmp = []
    for char in visited_cluster_exploration_method:
            if char in ["1","2"]:
                tmp.append(int(char))
            elif char != " ":
                print("Not a valid number - Aborting")
                return None
    visited_cluster_exploration_method = tmp

    tmp = []
    for char in RPB_selection_method:
            if char in ["1","2"]:
                tmp.append(int(char))
            elif char != " ":
                print("Not a valid number - Aborting")
                return None
    RPB_selection_method = tmp

    tmp = []
    for char in change_first:
            if char in ["1","2"]:
                tmp.append(int(char))
            elif char != " ":
                print("Not a valid number - Aborting")
                return None
    change_first = tmp

    tmp = []
    for char in anti_loop_method:
            if char in ["1","2"]:
                tmp.append(int(char))
            elif char != " ":
                print("Not a valid number - Aborting")
                return None
    anti_loop_method = tmp

    answers = { "history": answer_h,
                "pos_percentage": n_pos_percent,
                "nb_starting_angles": n_angle,
                "nb_rpb_min": n_rp_bots_min,
                "nb_rpb_max": n_rp_bots_max,
                "target_method": target_method,
                "cluster_exploration_method": cluster_exploration_method,
                "visited_cluster_exploration_method": visited_cluster_exploration_method,
                "RPB_selection_method": RPB_selection_method,
                "change_first": change_first,
                "anti_loop_method": anti_loop_method}

    return answers


def setup_sim(control,answers,recursive):

    history = answers["history"]
    if history == 'y':
        control.grid.no_history = False
    else:
        control.grid.no_history = True

    pos_percentage = answers["pos_percentage"]
    positions = control.grid.inside
    n_pos = len(positions)
    n_pos_sim = int(np.ceil(pos_percentage/100 * n_pos))

    n_angle = answers["nb_starting_angles"]

    n_rp_bots_max = answers["nb_rpb_max"]
    n_rp_bots_min = answers["nb_rpb_min"]

    target_method = answers["target_method"]
    cluster_exploration_method = answers["cluster_exploration_method"]
    visited_cluster_exploration_method = answers["visited_cluster_exploration_method"]
    RPB_selection_method = answers["RPB_selection_method"]
    change_first = answers["change_first"]
    anti_loop_method = answers["anti_loop_method"]

    
    # Calcul des différentes valeurs de positions initiales et angles initiaux
    if n_pos_sim < n_pos:
        rd.shuffle(positions)
        positions_sim = positions[:n_pos_sim]
    else :
        positions_sim = positions

    
    angles_sim = np.linspace(0, 2*np.pi/control.nbRefPointBots, n_angle+1)
    angles_sim = angles_sim[:-1]

    # Création de toutes les combinaisons uniques de paramètres
    method_params = []
    for t in target_method:
        for c in cluster_exploration_method:
            for v in visited_cluster_exploration_method:
                for R in RPB_selection_method:
                    for ch in change_first:
                        for a in anti_loop_method:
                            method_params.append((t,c,v,R,ch,a))

    parameters = []
    for pos in positions_sim:
        for angle in angles_sim:
            for nbRefPointBots in range(n_rp_bots_min,n_rp_bots_max + 1):
                for methods in method_params:
                    parameters.append((pos,angle,nbRefPointBots,methods))

    if not recursive:
        print("\n")
        print("The simulator will now attempt to run %s simulations." %len(parameters))
        input("Press Enter to start. ")

    return control, parameters


def multi_sim(control,parameters,filename):

    dirname = os.path.dirname(__file__)

    with open(os.path.join(dirname, "./results/",str(filename[8:-7])+"LOG.txt"), "w") as log:

        simulation_number = 1
        file_number = 1
        multiple_metrics = {'sim_number'    : [],
                            'start_pos'     : [],
                            'start_angle'   : [],
                            'nbRefPointBots': [],
                            'nbMeasurerBots': [],
                            'mb_exp_method' : [],
                            'rpb_exp_method': [],
                            'rpb_sel_method': [],
                            'first_loop'    : [],
                            'measuredTiles' : [],
                            'surface'       : [],
                            'pathLength'    : [],
                            'visitsPerTile' : [],
                            'history'       : [],
                            'sim_duration'  : []}

        ### Multiples simulations
        start = time.time()
        with click.progressbar(parameters) as bar:
            for params in bar:

                control_param = copy.deepcopy(control)
                metrics = launch_parametered_simulation(control_param,params)

                log.write("Simulation number %s done in %3.2f s\n" %(simulation_number,metrics["sim_duration"]))

                multiple_metrics['sim_number'].append(simulation_number)
                multiple_metrics['start_pos'].append(params[0])
                multiple_metrics['start_angle'].append(params[1])
                for key in metrics.keys():
                    if (key != 'history' and control.grid.no_history == True) or control.grid.no_history == False:
                        multiple_metrics[key].append(metrics[key])


                simulation_number += 1
                if simulation_number % 100 == 0: # Toutes les 100 simulations, on sauvegarde les résultats dans un gros fichier.
                    file = open(os.path.join(dirname, "./results/",str(filename[8:-7])+"-noGUI-results-"+str(file_number)+".pickle"), "wb")
                    pickle.dump(metrics, file)
                    file.close()

                    multiple_metrics = {'sim_number'    : [],
                                        'start_pos'     : [],
                                        'start_angle'   : [],
                                        'nbRefPointBots': [],
                                        'nbMeasurerBots': [],
                                        'mb_exp_method' : [],
                                        'rpb_exp_method': [],
                                        'rpb_sel_method': [],
                                        'first_loop'    : [],
                                        'measuredTiles' : [],
                                        'surface'       : [],
                                        'pathLength'    : [],
                                        'visitsPerTile' : [],
                                        'history'       : [],
                                        'sim_duration'  : []}
                    file_number += 1

        file = open(os.path.join(dirname, "./results/",str(filename[8:-7])+"-noGUI-results-"+str(file_number)+".pickle"), "wb")
        pickle.dump(metrics, file)
        file.close()

        print("Done in %3.2f seconds" %(time.time()-start))

        log.write("Simulations were all successfull")
        log.close()


if __name__ == "__main__":
    sim()