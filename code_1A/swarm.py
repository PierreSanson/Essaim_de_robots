import numpy as np
import random
from tkinter import *
import copy 


def default_shape(size): # on forme le plus petit carré pouvant contenir tous les robots et on le remplit avec ce qu'on a
    side = int(np.ceil(np.sqrt(size)))
    shape = np.zeros((side,side))
    count = 1
    for i in range(len(shape)):
        for j in range(len(shape[0])):
            if count <= size :
                shape[i,j] = count
                count += 1
            else :
                return shape
    return shape

def only_zero(liste):
    for k in liste :
        if k != 0:
            return False
    return True

def clean_shape(shape): # après le déplacement on efface les lignes ou colonnes vides sur les bords de l'essaim
    line_start = 0
    line_end = len(shape)-1
    column_start = 0
    column_end = len(shape[0])-1
    if only_zero(shape[0,:]):
        line_start += 1
    if only_zero(shape[line_end,:]):
        line_end -= 1
    if only_zero(shape[:,0]):
        column_start += 1
    if only_zero(shape[:,column_end]):
        column_end -= 1
    return shape[line_start:line_end+1,column_start:column_end+1]


def neighbours_coordinates(x,y,shape):
    nb_lines = len(shape)
    nb_columns = len(shape[0])
    neighbours_coordinates = []
    for (i,j,name) in [(x-1,y,"top"),(x+1,y,"bottom"),(x,y-1,"left"),(x,y+1,"right")]: # il faut vérifier que les voisins ne sortent pas de la grille
        if i>=0 and i<nb_lines and j>=0 and j<nb_columns:
            neighbours_coordinates.append((i,j,name))
    return neighbours_coordinates

def empty_border(shape): # étape préalable au déplacement : créer une matrice plus large pour éviter qu'un robot sorte des limites du tableau qui représente l'essaim
    dimensions = np.shape(shape)
    x, y = dimensions[0]+2, dimensions[1]+2
    new_shape = np.zeros((x,y))
    new_shape[1:x-1,1:y-1] = shape
    return new_shape

def conflict(list): # fonction intermédiaire pour la suivante, qui détecte la présence de 2 nombres non nuls différents dans une liste (True = conflit)
    a,b = 0,0
    for number in list :
        if number != 0 and a == 0:
            a = number
        if number != 0 and a != 0 and b == 0:
            b = number
    if a != b and b != 0 :
        return True

def conflict_check(shape_list): # fonction qui permet de vérifier qu'il n'y a pas de conflit entre les différentes roations effectuées en simultané (True = conflit)
    for i in range(len(shape_list[0])):
        for j in range(len(shape_list[0][0])):
            ij_values = []
            for n in range(len(shape_list)):
                ij_values.append(int(shape_list[0][i,j]))
            if conflict(ij_values):
                return True
    return False

def merge_steps(shape_list): # fonction qui fusionne toutes les modifications simultanées de la forme de l'essaim lors des rotaions, ATTENTION elle ne supprime pas les positions de départ des robots qui tourne, il faut le faire par dessus
   
    final_shape = np.zeros(np.shape(shape_list[0]))
    
    for i in range(len(shape_list[0])):
        for j in range(len(shape_list[0][0])):
            ij_values = []
            final_value = 0
            for n in range(len(shape_list)):
                ij_values.append(int(shape_list[n][i,j]))
            done = False
            c = 0
            while c < len(ij_values) and done == False:
                value = ij_values[c]
                if value != 0:
                    final_value = value
                    done = True
                c+=1
            final_shape[i,j] = final_value
    
    return final_shape

def clean_merge(new_shape,old_shape,moving_robots):
    for i in range(len(new_shape)):
        for j in range(len(new_shape[0])):
            if int(old_shape[i,j]) in moving_robots:
                new_shape[i,j] = 0
    return new_shape



class Robot:
 
    def __init__(self, number, swarm, I_min, N_I_max, k):
        
        self.number = number
        self.moved = False # un booléen dont j'ai besoin pour trouver un point fixe dans l'essaim quand je crée les images de l'essaim qui se déplace dans une salle pour le GUI
        self.neighbours = {"left":0,"right":0,"bottom":0,"top":0}# dictionnaire qui répertorie les noms des voisins qui se trouvent à gauche/droite (etc...) du robot dans l'image formée par l'essaim (orientation fixe)
        
        # définitions des caractéristiques du noeud
        self.I_min = I_min
        self.I_max = (2**N_I_max)*I_min
        self.I = I_min
        self.k = k
        self.grid_version = np.zeros((1,1))
        self.grid_robot = np.zeros((1,1))
        self.grid_robot[0] = self.number

        #grille visualisée par le robot restreinte à une taille 3*3
        self.shape = []

        self.c = 0
        i = random.random()
        self.tau = int((i+1)*self.I/2) # doit etre entier
        self.t = 0
        self.event = False # booléen permettant de repérer si une inconsistance avec les voisins du noeuds a été repérée
        # on utilise une file pour chaque noeud :
        # on traite les messages reçus instantanément et on ajoute les messages à envoyer à la file pour qu'ils soient envoyés au temps tau du noeud
        self.file = []
        self.list_neighbours = []
        self.init_grid(swarm)

        #statut du robot, 0 si il est dans la forme, 1 si il peut bouger, (2 si il est en attente)
        # inutilisé pour l'instant
        self.status = 0

        # liste qui doit contenir au plus une instruction (pour cette méthode), correspondant à la direction dans laquelle le robot doit aller si il doit bouger
        # inutilisé pour l'instant
        self.instructions = []

        self.superimposed_swarm = None

        #création des différentes situations dans lesquelles un robot peut bouger (méthode clock_wise)
        moving_shapes_top_left = [
                        [[0,1,0],
                        [0,1,0],
                        [0,0,0]],
                        [[0,1,1],
                        [0,1,0],
                        [0,0,0]],
                        [[0,1,1],
                        [0,1,1],
                        [0,0,0]],
                        [[0,1,1],
                        [0,1,0],
                        [0,0,1]],
                        [[0,1,1],
                        [0,1,1],
                        [0,1,1]],
                        [[0,1,1],
                        [0,1,1],
                        [0,0,1]],
                        [[0,1,1],
                        [0,1,1],
                        [1,1,1]]]
        moving_shapes_top = [
                        [[0,0,1],
                        [0,1,1],
                        [0,0,1]],
                        [[0,0,1],
                        [0,1,1],
                        [0,0,0]],
                        [[0,0,1],
                        [0,1,1],
                        [0,1,1]],
                        [[0,0,1],
                        [0,1,1],
                        [1,1,1]]]

        moving_shapes_top_right = []
        moving_shapes_bottom = []

        for shape in moving_shapes_top_left:
            moving_shapes_top_right.append(np.fliplr(np.array(shape)))
        for shape in moving_shapes_top:
            moving_shapes_bottom.append(np.fliplr(np.array(shape)))

                        

        moving_shape_one_step_cw = []
        moving_shape_two_steps_cw = []


        for shape in moving_shapes_top:
            moving_shape_one_step_cw.append(np.array(shape))
            moving_shape_one_step_cw.append(np.rot90(np.array(shape), 1))
            moving_shape_one_step_cw.append(np.rot90(np.array(shape), 2))
            moving_shape_one_step_cw.append(np.rot90(np.array(shape), 3))
        
        for shape in moving_shapes_top_left:
            moving_shape_two_steps_cw.append(np.array(shape))
            moving_shape_two_steps_cw.append(np.rot90(np.array(shape), 1))
            moving_shape_two_steps_cw.append(np.rot90(np.array(shape), 2))
            moving_shape_two_steps_cw.append(np.rot90(np.array(shape), 3))
        
        self.moving_shape_one_step_cw = moving_shape_one_step_cw
        self.moving_shape_two_steps_cw = moving_shape_two_steps_cw




        moving_shape_one_step_ccw = []
        moving_shape_two_steps_ccw = []
        
        for shape in moving_shapes_bottom:
            moving_shape_one_step_ccw.append(shape)
            moving_shape_one_step_ccw.append(np.rot90(shape, 1))
            moving_shape_one_step_ccw.append(np.rot90(shape, 2))
            moving_shape_one_step_ccw.append(np.rot90(shape, 3))
        
        for shape in moving_shapes_top_right:
            moving_shape_two_steps_ccw.append(shape)
            moving_shape_two_steps_ccw.append(np.rot90(shape, 1))
            moving_shape_two_steps_ccw.append(np.rot90(shape, 2))
            moving_shape_two_steps_ccw.append(np.rot90(shape, 3))
        
        self.moving_shape_one_step_ccw = moving_shape_one_step_ccw
        self.moving_shape_two_steps_ccw = moving_shape_two_steps_ccw    

        self.max_priority = (0, 0)
        self.priority = (0, self.number)

        self.sens = "cw"
        self.status = 1
        self.is_moving = [0,0]

    # initialisation de l'essaim vu par le robot
    def init_grid(self, global_grid):
        self.grid_version = np.zeros((3, 3))
        self.grid_robot = np.zeros((3, 3))
        self.grid_robot[1,1] = self.number
        self.grid_version[1,1] = 1
        neighbours_coordinates = self.define_neighbours(global_grid)
        for (i,j,number) in neighbours_coordinates:
            if  i==1 and j==0:
                self.list_neighbours.append(number)
                self.grid_robot[0][1] = number
                self.grid_version[0][1] += 1
            elif i==-1 and j==0:
                self.list_neighbours.append(number)
                self.grid_robot[2][1] = number
                self.grid_version[2][1] += 1
            elif i==0 and j==-1:
                self.list_neighbours.append(number)
                self.grid_robot[1][2] = number
                self.grid_version[1][2] += 1
            elif i==0 and j==1:
                self.list_neighbours.append(number)
                self.grid_robot[1][0] = number
                self.grid_version[1][0] += 1
        self.shape = copy.deepcopy(self.grid_robot.tolist())
        self.define_self_shape(self.shape)
    
    #fonction mettant à jour les voisins du robot après déplacement 
    def update_neighbours(self):
        list_neighbours = []
        center = int((len(self.grid_robot)-1)/2)
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i!=j:
                    if self.grid_robot[center+i,center+j]>0:
                        list_neighbours.append(self.grid_robot[center+i,center+j])

    # fonction mettant à jour la "shape" du robot, càd la grille 3x3 entourant le robot,
    # pour pouvoir la comparer aux différentes situations entraînant un mouvement (dépendant de la méthode choisie)
    def define_self_shape(self, shape):
        for i in range(3):
            for j in range(3):
                if  shape[i][j]== -1:
                    shape[i][j] = 0
                elif shape[i][j] > 0:
                    shape[i][j] = 1
    
    # fonction de mise à jour de la grille après réception d'un message d'un autre robot
    def update_grid(self, sender, received_grid_version, received_grid_robot):
        transmit = False
        len_received = len(received_grid_version)
        center_received = int((len_received-1)/2)
        len_self = len(self.grid_version)
        origin = [0,0]
        found_origin = False
        center = int((len_self-1)/2)
        should_compare = True
        for i in range(len_received):
            for j in range(len_received):
                if received_grid_robot[i,j] == self.number:
                    if received_grid_version[i,j] >= self.grid_version[center,center]:
                        origin[0] = i
                        origin[1] = j
                        found_origin = True
                    else : 
                        should_compare = False

        if not found_origin :
            should_compare = False

        for i in range(len_received):
            for j in range(len_received):
                len_self = len(self.grid_version)
                center = int((len_self-1)/2)
                x = center - origin[0] + i 
                y = center - origin[1] + j
                if 0 <= x < len_self and 0 <= y < len_self:
                    if ((received_grid_version[i,j] > self.grid_version[x, y] and should_compare) or (i == center_received and j == center_received)):
                        self.grid_robot[x,y] = received_grid_robot[i,j]
                        self.grid_version[x,y] = max(received_grid_version[i,j], self.grid_version[x,y])
                        self.event = True
                        transmit = True
                    elif received_grid_version[i,j] < self.grid_version[x, y]:
                        transmit = True
                        self.event = True
                    elif received_grid_version[i,j] == self.grid_version[x, y]:
                        self.c += 1
                elif received_grid_version[i,j] > 0 and should_compare:
                    
                    self.grid_version = self.add_element(received_grid_version[i,j], x, y, self.grid_version)
                    self.grid_robot = self.add_element(received_grid_robot[i,j], x, y, self.grid_robot)

        self.update_neighbours()

        if transmit or not should_compare: 
               # ajout du message à envoyer à la file du noeud
            if len(self.file) == 0 : self.file.append(sender)
     
    # fonction reformant l'essaim vu par le robot après un déplacement du robot
    def move_grid(self, grid, x, y, change_center = True):
        x = -x
        y = -y
        grid_height, grid_length = grid.shape
        start_row = 0
        start_col = 0
        end_row = grid_height - 1
        end_col = grid_length - 1

        while start_row < grid_length and np.array_equal(grid[start_row,:], np.zeros(grid_length)):
            start_row += 1
        while start_col < grid_height and np.array_equal(grid[:,start_col], np.zeros(grid_height)):
            start_col += 1

        while end_row > 0 and np.array_equal(grid[end_row,:], np.zeros(grid_length)):
            end_row -= 1
        while end_col > 0 and np.array_equal(grid[:,end_col], np.zeros(grid_height)):
            end_col -= 1

        expand = max(0, -x -start_row, -y -start_col, x - (grid_height - 1 - end_row), y - (grid_length - 1 - end_col))
        new_grid = np.zeros((grid_height + expand*2, grid_length + expand*2))

        center_grid = int((grid_height - 1)/2)
        center_new_grid = int((grid_height + expand*2 - 1)/2)
        number = grid[center_grid, center_grid]
        #grid[center_grid, center_grid] = 0
        new_grid[expand+x+start_row:expand+x+end_row+1, expand+y+start_col:expand+y+end_col+1] = grid[start_row:end_row+1, start_col:end_col+1]
        if change_center:
            new_grid[center_new_grid, center_new_grid] = number
            new_grid[center_new_grid+x, center_new_grid+y] = -1

        return new_grid

    # fonction ajoutant un robot à l'essaim vu par le robot en redimensionnant l'array si nécessaire
    def add_element(self, element, i, j, array):
        nb_lines = len(array)
        nb_columns = len(array[0])
        new_array = None
        if 0 <= i < nb_lines and 0 <= j < nb_columns:
            array[i,j] = element
            
        else:
            expand = max(i - nb_lines+1, j - nb_columns+1, -i, -j)
            new_array = np.zeros((nb_lines+expand*2, nb_lines+expand*2))
            size = len(new_array)
            new_array[expand:size-expand, expand:size-expand] = array
            array = new_array
            array[i+expand , j+expand] = element
        return array

    # fonction de définition initiale des voisins
    def define_neighbours(self, grid):
        nb_lines = len(grid)
        nb_columns = len(grid[0])
        x = 0
        y = 0
        for i in range(nb_lines):
            for j in range(nb_columns):
                if grid[i][j] == self.number:
                    x = i
                    y = j
        neighbours_coordinates = []
        for (i,j,name) in [(x-1,y,"top"),(x+1,y,"bottom"),(x,y-1,"left"),(x,y+1,"right")]: # il faut vérifier que les voisins ne sortent pas de la grille
            if i>=0 and i<nb_lines and j>=0 and j<nb_columns:
                if grid[i][j] != 0:
                    neighbours_coordinates.append((x-i, y-j, grid[i][j]))
        return neighbours_coordinates
    
    # fonction visant à trouver la meilleure superoposition de la forme voulue avec l'essaim actuel
    def find_best_pos(self, swarm, shape):
        # à n'executer qu'à l'initialisation de la formation, après la première recherche de la formation actuelle 
        # à optimiser
        def sum_superimposed(swarm, superimposed_shape):
            swarm_height, swarm_length = swarm.shape
            score = 0
            for i in range(swarm_height):
                for j in range(swarm_length):
                    if swarm[i, j] != 0 and superimposed_shape[i, j] == 1:
                        score+=1
            return score
        
        swarm_height, swarm_length = swarm.shape
        # start_row = 0
        # start_col = 0
        # end_row = swarm_length - 1
        # end_col = swarm_height - 1

        # while start_row < swarm_length and np.array_equal(swarm[start_row,:], np.zeros(swarm_length)):
        #     start_row += 1
        # while start_col < swarm_height and np.array_equal(swarm[:,start_col], np.zeros(swarm_height)):
        #     start_col += 1

        # while end_row > 0 and np.array_equal(swarm[end_row,:], np.zeros(swarm_length)):
        #     end_row -= 1
        # while end_col > 0 and np.array_equal(swarm[:,end_col], np.zeros(swarm_height)):
        #     end_col -= 1

        # self.offset = [end_row, end_col]

        # new_swarm = np.zeros((3*(end_row-start_row+1), 3*(end_col-start_col+1)))
        # new_swarm[end_row-start_row+1:2*(end_row-start_row+1), end_col-start_col+1:2*(end_col-start_col+1)] = swarm[start_row:end_row+1, start_col:end_col+1]
        # new_swarm_height, new_swarm_length = new_swarm.shape
        # print(swarm[start_row:end_row+1, start_col:end_col+1])
        # print(new_swarm)
        # print(center + end_row, center + end_col)
        # print(new_swarm[end_row, end_col])
        new_swarm = np.zeros((3*(swarm_height + 1), 3*(swarm_length + 1)))
        new_swarm_height, new_swarm_length = new_swarm.shape
        center_swarm = int((swarm_length-1)/2)
        center_new_swarm = int((new_swarm_length-1)/2)
        new_swarm[center_new_swarm-center_swarm:center_new_swarm+center_swarm+1, center_new_swarm-center_swarm:center_new_swarm+center_swarm+1] = swarm
        shape_left = np.rot90(shape, 1)
        shape_bottom = np.rot90(shape, 2)
        shape_right = np.rot90(shape, 3)
        shape_height, shape_length = shape.shape
        
        superimposed_shape = np.zeros(new_swarm.shape)
        best_shape = None
        max_sup = 0
        rot_max = 4

        for i in range(new_swarm_height-shape_height+1):
            for j in range(new_swarm_length-shape_length+1) :
                superimposed_shape[i:i+shape_height, j:j+shape_length] = shape
                sup = sum_superimposed(new_swarm, superimposed_shape)
                if sup > max_sup or (sup == max_sup and rot_max > 0) :
                    rot_max = 0
                    best_shape = superimposed_shape
                    max_sup = sup
                superimposed_shape = np.zeros(new_swarm.shape)
                superimposed_shape[i:i+shape_height, j:j+shape_length] = shape_bottom
                sup = sum_superimposed(new_swarm, superimposed_shape)
                if sup > max_sup or (sup == max_sup and rot_max > 2):
                    rot_max = 2
                    best_shape = superimposed_shape
                    max_sup = sup
                superimposed_shape = np.zeros(new_swarm.shape)
        for i in range(new_swarm_height-shape_length+1):
            for j in range(new_swarm_length-shape_height+1) :
                superimposed_shape[i:i+shape_length, j:j+shape_height] = shape_left
                sup = sum_superimposed(new_swarm, superimposed_shape)
                if sup > max_sup or (sup == max_sup and rot_max > 1):
                    rot_max = 1
                    best_shape = superimposed_shape
                    max_sup = sup
                superimposed_shape = np.zeros(new_swarm.shape)
                superimposed_shape[i:i+shape_length, j:j+shape_height] = shape_right
                sup = sum_superimposed(new_swarm, superimposed_shape)
                if sup > max_sup or (sup == max_sup and rot_max > 3):
                    rot_max = 3
                    best_shape = superimposed_shape
                    max_sup = sup
                superimposed_shape = np.zeros(new_swarm.shape)
        best_shape_height, best_shape_length = best_shape.shape
        start_row = 0
        start_col = 0
        end_row = best_shape_length - 1
        end_col = best_shape_height - 1

        while start_row < best_shape_length and np.array_equal(best_shape[start_row,:], np.zeros(best_shape_length)):
            start_row += 1
        while start_col < best_shape_height and np.array_equal(best_shape[:,start_col], np.zeros(best_shape_height)):
            start_col += 1

        while end_row > 0 and np.array_equal(best_shape[end_row,:], np.zeros(best_shape_length)):
            end_row -= 1
        while end_col > 0 and np.array_equal(best_shape[:,end_col], np.zeros(best_shape_height)):
            end_col -= 1

        cut = min(start_row-1, start_col-1, best_shape_height-end_row-1, best_shape_length-end_col-1)

        return best_shape

    # fonctionnant déterminant si le robot doit bouger (méthode clockwise)
    def should_move_clockwise(self):
        found = False
        instruction = None
        center = int((len(self.grid_robot)-1)/2)
        self.shape = copy.deepcopy(self.grid_robot[center-1:center+2, center-1:center+2].tolist())
        self.define_self_shape(self.shape)
        for (i, shape) in enumerate(self.moving_shape_one_step_cw):
            if np.array_equal(self.shape, shape):
                if i%4 == 0:
                    instruction = 'top'
                if i%4 == 1:
                    instruction = 'left'
                if i%4 == 2:
                    instruction = 'bottom'
                if i%4 == 3:
                    instruction = 'right'
                found = True
                # print(self.shape)
                # print(instruction)
        if not found:
            for (i, shape) in enumerate(self.moving_shape_two_steps_cw):
                if np.array_equal(self.shape, shape):
                    if i%4 == 0:
                        instruction = 'top_left'
                    if i%4 == 1:
                        instruction = 'bottom_left'
                    if i%4 == 2:
                        instruction = 'bottom_right'
                    if i%4 == 3:
                        instruction = 'top_right'
        #             print(self.shape)
        #             print(instruction)
        # print("instruction : ", instruction)
        return instruction

    # fonction initialisant la séquence de formation (peut être généralisée à toutes méthodes)
    def formation_init(self, swarm, shape):
        self.superimposed_swarm = self.find_best_pos(swarm, shape)
    
    # fonction vérifiant si le robot est en place ou non
    def check_formation_clockwise(self):
        heigth, length = self.superimposed_swarm.shape
        center = int((heigth-1)/2)
        if self.superimposed_swarm[center, center] == 0:
            #print(self.number, "pas en place")
            instruction = self.should_move_clockwise()
            return instruction
        #print(self.number, "en place")
        return None

    # fonction de déplacement des robots (toutes méthodes)
    def move(self, method = 'clockwise'):
        move = None
        if method == 'clockwise':
            instruction = self.check_formation_clockwise()
        if method == 'v2':
            center = int((len(self.superimposed_swarm.shape)-1)/2)
            if self.superimposed_swarm[center, center] == 0:
                instruction = self.should_move_v2(self.sens, self.shape, self.grid_robot)
            else :
                instruction = None
                self.status = 0
        if instruction != None and (self.status == 2 or self.check_priority()):
            self.status = 2
            self.event = True
            x = 0
            y = 0
            if instruction == 'top' :
                x = -1
                y = 0
            if instruction == 'left':
                x = 0
                y = -1
            if instruction == 'bottom':
                x = 1
                y = 0
            if instruction == 'right':
                x = 0
                y = 1
            if instruction == 'top_left':
                x = -1
                y = -1
            if instruction == 'bottom_left':
                x = 1
                y = -1
            if instruction == 'bottom_right':
                x = 1
                y = 1
            if instruction == 'top_right':
                x = -1
                y = 1
            if x!=0 or y!=0:
                move = [self.number, instruction]
            self.grid_robot = self.move_grid(self.grid_robot, x, y)
            self.grid_version = self.move_grid(self.grid_version, x, y, change_center=False)
            center = int((len(self.grid_version) - 1)/2)
            self.grid_version[center, center] = max(self.grid_version[center-x, center-y] + 1, self.grid_version[center, center] + 1)
            self.grid_version[center-x, center-y] += 1
            self.superimposed_swarm = self.move_grid(self.superimposed_swarm, x, y, change_center = False)
            if method == 'v2':
                center = int((len(self.superimposed_swarm) - 1)/2)
                if self.superimposed_swarm[center, center] == 1:
                    self.status = 0
                    self.is_moving[1] += 1
                    self.is_moving[0] = 0
            self.update_neighbours()

        return move

    def update_priority_clockwise(self, received_priority):
        if received_priority[1] > self.max_priority[1]:
            self.max_priority = received_priority
            self.event = True
            self.file.append(self.number)
    
    def check_priority(self):
        if self.priority[1] == self.max_priority[1]:
            self.is_moving[1] += 1
            self.is_moving[0] = self.number
            return True
        return False

    def reset_priority(self):
        self.max_priority = (0, 0)
        self.priority = (0, self.number)
    

    def should_move_v2(self, sens, shape, grid_robot):
        found = False
        instruction = None
        center = int((len(grid_robot)-1)/2)
        shape = copy.deepcopy(grid_robot[center-1:center+2, center-1:center+2].tolist())
        self.define_self_shape(shape)
        if sens == "cw":
            for (i, model_shape) in enumerate(self.moving_shape_one_step_cw):
                if np.array_equal(shape, model_shape):
                    if i%4 == 0:
                        instruction = 'top'
                    if i%4 == 1:
                        instruction = 'left'
                    if i%4 == 2:
                        instruction = 'bottom'
                    if i%4 == 3:
                        instruction = 'right'
                    found = True
            if not found:
                for (i, model_shape) in enumerate(self.moving_shape_two_steps_cw):
                    if np.array_equal(shape, model_shape):
                        if i%4 == 0:
                            instruction = 'top_left'
                        if i%4 == 1:
                            instruction = 'bottom_left'
                        if i%4 == 2:
                            instruction = 'bottom_right'
                        if i%4 == 3:
                            instruction = 'top_right'
        elif sens == "ccw":
            for (i, model_shape) in enumerate(self.moving_shape_one_step_ccw):
                if np.array_equal(shape, model_shape):
                    if i%4 == 0:
                        instruction = 'top'
                    if i%4 == 1:
                        instruction = 'left'
                    if i%4 == 2:
                        instruction = 'bottom'
                    if i%4 == 3:
                        instruction = 'right'
                    found = True
            if not found:
                for (i, model_shape) in enumerate(self.moving_shape_two_steps_ccw):
                    if np.array_equal(shape, model_shape):
                        if i%4 == 0:
                            instruction = 'top_right'
                        if i%4 == 1:
                            instruction = 'top_left'
                        if i%4 == 2:
                            instruction = 'bottom_left'
                        if i%4 == 3:
                            instruction = 'bottom_right'
        return instruction

    def temporary_move(self, instruction, superimposed_swarm, grid_robot):
        if instruction != None:
            x = 0
            y = 0
            if instruction == 'top' :
                x = -1
                y = 0
            if instruction == 'left':
                x = 0
                y = -1
            if instruction == 'bottom':
                x = 1
                y = 0
            if instruction == 'right':
                x = 0
                y = 1
            if instruction == 'top_left':
                x = -1
                y = -1
            if instruction == 'bottom_left':
                x = 1
                y = -1
            if instruction == 'bottom_right':
                x = 1
                y = 1
            if instruction == 'top_right':
                x = -1
                y = 1

            grid_robot = self.move_grid(grid_robot, x, y)
            superimposed_swarm = self.move_grid(superimposed_swarm, x, y, change_center = False)
            return superimposed_swarm, grid_robot

    def find_shortest_path_v2(self, limit = 100):
        shortest_path_cw = None
        temporary_superimposed_swarm = copy.deepcopy(self.superimposed_swarm)
        temporary_shape = copy.deepcopy(self.shape)
        temporary_grid_robot = copy.deepcopy(self.grid_robot)
        center = int((len(temporary_superimposed_swarm)-1)/2)
        i=0
        while temporary_superimposed_swarm[center,center] != 1 and i < limit:
            instruction = self.should_move_v2("cw", temporary_shape, temporary_grid_robot)
            if instruction != None:
                temporary_superimposed_swarm, temporary_grid_robot = self.temporary_move(instruction, temporary_superimposed_swarm, temporary_grid_robot)
                if shortest_path_cw == None:
                    shortest_path_cw = 1
                else :
                    shortest_path_cw += 1
            else:
                break
            i+=1
        if temporary_superimposed_swarm[center,center] != 1:
            shortest_path_cw = None
        shortest_path_ccw = None
        temporary_superimposed_swarm = copy.deepcopy(self.superimposed_swarm)
        temporary_shape = copy.deepcopy(self.shape)
        temporary_grid_robot = copy.deepcopy(self.grid_robot)
        center = int((len(temporary_superimposed_swarm)-1)/2)
        i=0
        while temporary_superimposed_swarm[center,center] != 1 and i < limit:
            instruction = self.should_move_v2("ccw", temporary_shape, temporary_grid_robot)
            if instruction != None:
                temporary_superimposed_swarm, temporary_grid_robot = self.temporary_move(instruction, temporary_superimposed_swarm, temporary_grid_robot)
                if shortest_path_ccw == None:
                    shortest_path_ccw = 1
                else :
                    shortest_path_ccw += 1
            else:
                break
            i+=1
        
        if temporary_superimposed_swarm[center,center] != 1:
            shortest_path_ccw = None

        if shortest_path_cw == None and shortest_path_ccw == None:
            return None
        elif shortest_path_ccw == None:
            return (shortest_path_cw, "cw")
        elif shortest_path_cw == None:
            return (shortest_path_ccw, "ccw")
        elif shortest_path_cw <= shortest_path_ccw:
            return (shortest_path_cw, "cw")
        else:
            return (shortest_path_ccw, "ccw")
        
    def define_priority_v2(self):
        shortest_path = self.find_shortest_path_v2()
        if shortest_path != None:
            self.priority = (shortest_path[0], self.number)
            self.sens = shortest_path[1]

    def update_priority_v2(self, received_priority):
        if received_priority[0] > 0 and (self.max_priority[0] == 0 or received_priority[0] < self.max_priority[0] or (received_priority[0] == self.max_priority[0] and received_priority[1] > self.max_priority[1])):
            self.max_priority = received_priority
            self.event = True
            self.file.append(self.number)
    
    def update_is_moving(self, received_is_moving):
        if received_is_moving[1] > self.is_moving[1]:
            self.is_moving = received_is_moving
            self.event = True
            self.file.append(self.number)





class Swarm:
    def __init__(self,size,shape = []): 
        self.size = size # nombre de robots dans l'essaim
        if len(shape) == 0 :
            self.shape = np.array(default_shape(size)) # matrice qui représente la position de tous les robots dans l'essaim par la présence de leur numéro dans une case
            shape = self.shape.tolist()
        else :
            self.shape = np.array(shape)
        self.robots = {} # dictionnaire qui répertorie tous les robots de l'essaim avec en clé leur numéro et en élément l'objet Robot qui lui est associé
        for number in range(1,size+1):
            self.robots[number] = Robot(number, shape, 10, 4, 10)
        self.global_t = 0
        self.moves_sequence = []

    # entame de la séquence de formation (fonction type main)
    def main_sequence(self, shape, iterations, nb_init, nb_wait_exchange, formation_method = 'v2'):
        #initialisation des cartes de chacun des robots
        print("initialisation des cartes de chacun des robots...")
        for i in range(nb_init):
            self.update()
        if formation_method == 'clockwise':
            # définition de la forme à former pour chaque robot (leeeeeeeent)
            print("définition de la forme à former pour chaque robot...")
            for n in self.robots:
                self.robots[n].formation_init(self.robots[n].grid_robot, shape)
            #initialisation de la séquence de formation clockwise pour chacun des robots
            print("initialisation de la séquence de formation clockwise pour chacun des robots...")
            self.move_robots_clockwise_sequence(self.robots, iterations, nb_wait_exchange, shape)
            print("Done!(?)")
            # for robot in self.robots:
            #     print(self.robots[robot].superimposed_swarm)
            # for robot in self.robots:
            #     print('robots ',robot, self.robots[robot].grid_robot)

        elif formation_method == 'v2':
            # définition de la forme à former pour chaque robot (leeeeeeeent)
            print("définition de la forme à former pour chaque robot...")
            for n in self.robots:
                self.robots[n].formation_init(self.robots[n].grid_robot, shape)
            #initialisation de la séquence de formation clockwise pour chacun des robots
            print("initialisation de la séquence de formation v2 pour chacun des robots...")
            self.move_robots_v2_sequence(self.robots, iterations, nb_wait_exchange, shape)
            print("Done!(?)")
            # for robot in self.robots:
            #     print('robots ',robot, self.robots[robot].superimposed_swarm)
            # for robot in self.robots:
            #     print('robots ',robot, self.robots[robot].grid_robot)
            
    # sequence de formation clockwise
    def move_robots_clockwise_sequence(self, robots, iterations, nb_wait_exchange, shape):
        for i in range(iterations):
            for n in robots :
                self.robots[n].reset_priority()
            for n in robots :
                if self.robots[n].check_formation_clockwise() != None:
                    self.transmit(self.robots[n], "init_priority_clockwise")
            for k in range (nb_wait_exchange):
                self.update(message_type="priority_clockwise")
            for n in robots:
                move = robots[n].move()
                if move != None:
                    self.transmit(robots[n],"position")
                    self.moves_sequence.append([tuple(move)])
            for j in range(nb_wait_exchange):
                self.update()

    def move_robots_v2_sequence(self, robots, iterations, nb_wait_exchange, shape):
        for i in range(iterations):

            for n in robots :
                if self.robots[n].is_moving[0] == 0:
                    self.robots[n].reset_priority()
                    self.robots[n].define_priority_v2()
            for n in robots :
                if self.robots[n].is_moving[0] == 0:
                    if self.robots[n].priority[0] != 0:
                        self.transmit(self.robots[n], "init_priority_v2")
            for k in range (nb_wait_exchange):
                self.update(message_type="priority_v2")
            for n in robots:
                move = robots[n].move(method = 'v2')
                if move != None:
                    self.transmit(robots[n],"position")
                    self.moves_sequence.append([tuple(move)])
            for j in range(nb_wait_exchange):
                self.update()
            for k in range (nb_wait_exchange):
                self.update(message_type="is_moving")


    def update_neighbours(self):
        for number in self.robots.keys():
            x_robot = np.where(self.shape==number)[0][0] # acquisition des coordonnées du robot
            y_robot = np.where(self.shape==number)[1][0]
            for (x,y,name) in neighbours_coordinates(x_robot,y_robot,self.shape):
                self.robots[number].neighbours[name] = int(self.shape[x,y])
    
    def transmit(self,robot, message_type):
        #print("messsage de " + str(robot.number) + " au temps ", robot.t)
        if message_type == "position":
            for v in robot.list_neighbours:
                    self.robots[v].update_grid(robot.number, robot.grid_version, robot.grid_robot)
        elif message_type == "priority_clockwise":
            for v in robot.list_neighbours:
                    self.robots[v].update_priority_clockwise(robot.max_priority)
        elif message_type == "init_priority_clockwise":
            for v in robot.list_neighbours:
                    self.robots[v].update_priority_clockwise((robot.number, robot.number))
        elif message_type == "priority_v2":
            for v in robot.list_neighbours:
                    self.robots[v].update_priority_v2(robot.max_priority)
        elif message_type == "init_priority_v2":
            for v in robot.list_neighbours:
                    self.robots[v].update_priority_v2(robot.priority)
        elif message_type == "is_moving":
            for v in robot.list_neighbours:
                    self.robots[v].update_is_moving(robot.is_moving)
        
    def update(self, message_type = "position"):
        for n in self.robots:
            if self.robots[n].t > self.robots[n].I:
                # on définit un nouveau I pour le noeud n
                if not self.robots[n].event:
                    self.robots[n].I = min(self.robots[n].I_max, 2*self.robots[n].I)
                else :
                    self.robots[n].I = self.robots[n].I_min
                    self.robots[n].event = False
                # on définit un nouveau tau pour le noeud n 
                self.robots[n].tau = int((random.random()+1)*self.robots[n].I/2)
                #print('tau de', str(self.robots[n].number) ,':', self.robots[n].tau)
                # on remet à 0 le t local du noeud et son compteur de redondance c
                self.robots[n].t = 0
                self.robots[n].c = 0
            elif self.robots[n].t == self.robots[n].tau :
                # les messages ne peuvent s'envoyer qu'au temps tau du noeud
                # on traite tous les messages à envoyer avant de passer au t suivant
                if self.robots[n].c < self.robots[n].k :
                    self.transmit(self.robots[n], message_type)
                while len(self.robots[n].file) > 0:
                    self.transmit(self.robots[n], message_type)
                    #print(len(self.robots[n].file))
                    self.robots[n].file.pop(0)
        # on incrémente le t de chaque noeud
        for n in self.robots:
            self.robots[n].t += 1
        self.global_t += 1

    def rotation(self,robot_tourne,robot_fixe,direction): # direction = 1 pour rotation trigo, direction = -1 pour rotation horaire
        if not robot_fixe in self.robots[robot_tourne].neighbours.values():
            print("Impossible") # on vérifie que le voisin autour duquel on veut tourner est bien là
        else :
            shape = empty_border(self.shape)
            y_voisin = np.where(shape==robot_fixe)[0][0]
            x_voisin = np.where(shape==robot_fixe)[1][0]
            y_robot = np.where(shape==robot_tourne)[0][0]
            x_robot = np.where(shape==robot_tourne)[1][0]
            if direction == 1 :
                new_x = (y_robot-y_voisin) + x_voisin # on applique matrice de rotation en prenant pour origine le voisin qui nous intéresse
                new_y = -1*(x_robot-x_voisin) + y_voisin 
            if direction == -1 :
                new_x = -1*(y_robot-y_voisin) + x_voisin
                new_y = (x_robot-x_voisin) + y_voisin
            if shape[new_y,new_x] != 0 :
                print("Impossible") # on vérifie que l'endroit où on veut aller est libre
            else :
                mid_x = (new_x - x_voisin) + (x_robot- x_voisin) + x_voisin # somme des positions relatives au voisin pour "moyenner" le déplacement + coordonnée de l'origine
                mid_y = (new_y - y_voisin) + (y_robot- y_voisin) + y_voisin

                shape[new_y,new_x] = robot_tourne
                shape[y_robot,x_robot] = 0
               
                return shape, mid_x, mid_y, new_x, new_y
        
    def translation(self,robot_bouge,robot_fixe,direction): # la direction est "top/bottom/left/right", et on utilise les informations sur les voisins du robot fixe pour voir si c'est possible
        if not robot_fixe in self.robots[robot_bouge].neighbours.values():
            print("Impossible") # on vérifie que le voisin le long duquel on veut translater est bien là
        else :
            shape = empty_border(self.shape)
            y_robot = np.where(shape==robot_bouge)[0][0]
            x_robot = np.where(shape==robot_bouge)[1][0]
            is_ok = False
            if direction == "top" and shape[y_robot-1,x_robot] == 0 and self.robots[robot_fixe].neighbours["top"] != 0 :
                new_y = y_robot-1
                new_x = x_robot
                is_ok = True
            elif direction == "bottom" and shape[y_robot+1,x_robot] == 0 and self.robots[robot_fixe].neighbours["bottom"] != 0 :
                new_y = y_robot+1
                new_x = x_robot
                is_ok = True
            elif direction == "left" and shape[y_robot,x_robot-1] == 0 and self.robots[robot_fixe].neighbours["left"] != 0 :
                new_y = y_robot
                new_x = x_robot-1
                is_ok = True
            elif direction == "right" and shape[y_robot,x_robot+1] == 0 and self.robots[robot_fixe].neighbours["right"] != 0 :
                new_y = y_robot
                new_x = x_robot+1
                is_ok = True
            else :
                print("Impossible")
            if is_ok :
                shape[new_y,new_x] = robot_bouge
                shape[y_robot,x_robot] = 0

        shape = clean_shape(shape)
        shape = clean_shape(shape) # on doit fairer le nettoyage 2 fois car à l'issue de la translation on peut avoir 2 lignes ou colonnes vides
        self.shape = shape
    
    def available_directions(self,robot):

        self.shape = empty_border(self.shape)
        self.update_neighbours()
        available = []

        if self.robots[robot].neighbours["left"] != 0 :
            # vérification pour translations
            if self.robots[self.robots[robot].neighbours["left"]].neighbours["top"] != 0 and self.robots[robot].neighbours["top"] == 0 :
                available.append("top")
            if self.robots[self.robots[robot].neighbours["left"]].neighbours["bottom"] != 0 and self.robots[robot].neighbours["bottom"] == 0 :
                available.append("bottom")
            # vérification pour rotation
            if self.robots[self.robots[robot].neighbours["left"]].neighbours["bottom"] == 0 and self.robots[robot].neighbours["bottom"] == 0 :
                available.append("bottom_left")
            if self.robots[self.robots[robot].neighbours["left"]].neighbours["top"] == 0 and self.robots[robot].neighbours["top"] == 0 :
                available.append("top_left")
    
        if self.robots[robot].neighbours["right"] != 0 :
            # vérification pour translations
            if self.robots[self.robots[robot].neighbours["right"]].neighbours["top"] != 0 and self.robots[robot].neighbours["top"] == 0 :
                available.append("top")
            if self.robots[self.robots[robot].neighbours["right"]].neighbours["bottom"] != 0 and self.robots[robot].neighbours["bottom"] == 0 :
                available.append("bottom")
            # vérification pour rotation
            if self.robots[self.robots[robot].neighbours["right"]].neighbours["bottom"] == 0 and self.robots[robot].neighbours["bottom"] == 0 :
                available.append("bottom_right")
            if self.robots[self.robots[robot].neighbours["right"]].neighbours["top"] == 0 and self.robots[robot].neighbours["top"] == 0 :
                available.append("top_right")

        if self.robots[robot].neighbours["top"] != 0 :
            # vérification pour translations
            if self.robots[self.robots[robot].neighbours["top"]].neighbours["right"] != 0 and self.robots[robot].neighbours["right"] == 0 :
                available.append("right")
            if self.robots[self.robots[robot].neighbours["top"]].neighbours["left"] != 0 and self.robots[robot].neighbours["left"] == 0 :
                available.append("left")
            # vérification pour rotation
            if self.robots[self.robots[robot].neighbours["top"]].neighbours["left"] == 0 and self.robots[robot].neighbours["left"] == 0 :
                available.append("top_left")
            if self.robots[self.robots[robot].neighbours["top"]].neighbours["right"] == 0 and self.robots[robot].neighbours["right"] == 0 :
                available.append("top_right")

        if self.robots[robot].neighbours["bottom"] != 0 :
            # vérification pour translations
            if self.robots[self.robots[robot].neighbours["bottom"]].neighbours["right"] != 0 and self.robots[robot].neighbours["right"] == 0 :
                available.append("right")
            if self.robots[self.robots[robot].neighbours["bottom"]].neighbours["left"] != 0 and self.robots[robot].neighbours["left"] == 0 :
                available.append("left")
            # vérification pour rotation
            if self.robots[self.robots[robot].neighbours["bottom"]].neighbours["left"] == 0 and self.robots[robot].neighbours["left"] == 0 :
                available.append("bottom_left")
            if self.robots[self.robots[robot].neighbours["bottom"]].neighbours["right"] == 0 and self.robots[robot].neighbours["right"] == 0 :
                available.append("bottom_right")

        self.shape = clean_shape(self.shape)
        available = list(set(available))
        return available

    def direction_to_rotation(self,robot,direction): # prend en entrée un robot et une direction (ex:"top") et renvoie le point de roration et le sens de rotation associé
        
        if direction == "top_left":
            if self.robots[robot].neighbours["left"] != 0 :
                sens = 1
                robot_fixe = self.robots[robot].neighbours["left"]
            else :
                sens = -1
                robot_fixe = self.robots[robot].neighbours["top"]
        
        if direction == "top_right":
            if self.robots[robot].neighbours["top"] != 0 :
                sens = 1
                robot_fixe = self.robots[robot].neighbours["top"]
            else :
                sens = -1
                robot_fixe = self.robots[robot].neighbours["right"]
        
        if direction == "bottom_right":
            if self.robots[robot].neighbours["right"] != 0 :
                sens = 1
                robot_fixe = self.robots[robot].neighbours["right"]
            else :
                sens = -1
                robot_fixe = self.robots[robot].neighbours["bottom"]
        
        if direction == "bottom_left":
            if self.robots[robot].neighbours["bottom"] != 0 :
                sens = 1
                robot_fixe = self.robots[robot].neighbours["bottom"]
            else :
                sens = -1
                robot_fixe = self.robots[robot].neighbours["left"]

        return robot_fixe,sens

    def direction_to_translation(self,robot,direction): # renvoie le numéro du robot_fixe
        if direction in ["top","bottom"]:
            if self.robots[robot].neighbours["left"] != 0:
                if self.robots[self.robots[robot].neighbours["left"]].neighbours[direction] != 0:
                    return self.robots[robot].neighbours["left"]
            elif self.robots[robot].neighbours["right"] != 0:
                if self.robots[self.robots[robot].neighbours["right"]].neighbours[direction] != 0:
                    return self.robots[robot].neighbours["right"]

        if direction in ["right","left"]:
            if self.robots[robot].neighbours["bottom"] != 0:
                if self.robots[self.robots[robot].neighbours["bottom"]].neighbours[direction] != 0:
                    return self.robots[robot].neighbours["bottom"]
            elif self.robots[robot].neighbours["top"] != 0:
                if self.robots[self.robots[robot].neighbours["top"]].neighbours[direction] != 0:
                    return self.robots[robot].neighbours["top"]

    def move(self,instructions): # liste d'instructions à exécuter en simultané [(robot,dir),(robot,dir)...]
        swarm_states = [] # liste qui va contenir 1 ou 2 états de l'essaim (en fonction de la présence d'un mouvement en deux temps ou non) et qui sera utilisée pour faire l'affichage graphique
        translations = [] # on sépare les instructions en deux catégories, les translations seront effectuées en premier car elles ne prennent qu'une étape et on pourra ainsi déterminer s'il y a conflit ou non
        rotations = [] # REMARQUE : dans son état actuel la fonction considère qu'on ne donne d'instructions que lorsque les mouvements demandés sont finis, c'est à dire qu'on ne rajoute pas de consignes alors que des robots sont encore en train de bouger
        

        translations_for_GUI = []
        rotations_for_GUI = []

        for (robot_move,direction) in instructions:

            if direction not in ["left","top_left","top","top_right","right","bottom_right","bottom","bottom_left"]:
                print("Commande invalide")
                return None

            if direction in ["left","top","right","bottom"]:
                translations.append((robot_move,direction))
            
            if direction in ["top_left","top_right","bottom_right","bottom_left"]:
                rotations.append((robot_move,direction))

        for (robot_move,direction) in translations:       
            if direction not in self.available_directions(robot_move):
                print("Translation impossible")
                return None

            robot_fixe = self.direction_to_translation(robot_move,direction)
            self.robots[robot_move].moved = True
            self.translation(robot_move,robot_fixe,direction)
            translations_for_GUI.append((robot_move,robot_fixe,direction))

        first_steps = []
        second_steps = []
        moving_robots = []
        old_shape = empty_border(self.shape)

        for (robot_move,direction) in rotations:
            moving_robots.append(robot_move)
            if direction not in self.available_directions(robot_move):
                print("Rotation impossible")
                return None

            robot_fixe,sens = self.direction_to_rotation(robot_move,direction)
            rotations_for_GUI.append((robot_move,robot_fixe,sens))
            self.robots[robot_move].moved = True
            shape2, mid_x, mid_y, new_x, new_y = self.rotation(robot_move,robot_fixe,sens)
            shape1 = np.copy(shape2)
            shape1[new_y,new_x] = 0
            shape1[mid_y,mid_x] = robot_move
            
            first_steps.append(shape1)
            second_steps.append(shape2)

        if rotations == []:
            swarm_states.append(self.shape)
            return swarm_states, translations_for_GUI, rotations_for_GUI

        elif conflict_check(first_steps) or conflict_check(second_steps):
            print("Conflit dans les rotations, déplacement impossible")
            return None
        else:
            first_state = merge_steps(first_steps)
            first_state = clean_merge(first_state,old_shape,moving_robots)
            first_state = clean_shape(clean_shape(first_state))
            swarm_states.append(first_state)

            second_state = merge_steps(second_steps)
            second_state = clean_merge(second_state,old_shape,moving_robots)
            second_state = clean_shape(clean_shape(second_state))
            swarm_states.append(second_state)

            self.shape = swarm_states[-1]
            return swarm_states, translations_for_GUI, rotations_for_GUI


    def reset_moved(self):
        for robot in self.robots.values():
            robot.moved = False

    
    def find_fixe(self):
        for robot in self.robots.values():
            if robot.moved == False:
                return robot.number
            
    
if __name__ == "__main__":
    swarm = [[7, 10, 6, 5, 0, 0],
            [0, 3, 4, 1, 8, 0],
            [0, 9, 2, 0, 0, 0], 
            [0, 0, 0, 0, 0, 0]]
    swarm = np.array(swarm)
    shape = [[0, 0, 1, 1, 1],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 1, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 1, 1]]
    shape = np.array(shape)

    S = Swarm(10,  swarm)
    S.main_sequence(shape, 50, 100, 50, formation_method="clockwise")
    print(S.moves_sequence)



""" # test de création d'essaim avec forme par défaut
S = Swarm(8)
print(S.size)
for number in S.robots.keys():
    print(number, S.robots[number].neighbours)
print(S.shape)        

S.update_neighbours()
for number in S.robots.keys():
    print(number, S.robots[number].neighbours)
"""

"""
 # test de création d'essaim avec forme perso
size, shape = define_shape(6)
S = Swarm(size,shape)
S.update_neighbours()
print(S.size)
for number in S.robots.keys():
    print(number, S.robots[number].neighbours)
print(S.shape)   
"""

""" # test de rotation
S = Swarm(8)
print(S.shape)
S.update_neighbours()
S.rotation(3,2,1)
print(S.shape)
"""

""" # test de translation
S = Swarm(6,np.array([[1,0,0],[2,3,0],[4,5,6]]))
S.update_neighbours()
S.translation(1,2,"right")
print(S.shape)
S.update_neighbours()
S.translation(6,5,"up")
print(S.shape)
"""

""" # test available_direction
size, shape = define_shape(3)
S = Swarm(size,shape)
print(S.shape)
S.update_neighbours()
robot = 4
print(S.robots[robot].neighbours)
print(S.available_directions(robot))
"""

""" # test mouvement universel
S = Swarm(9)
instructions = [(4,"top_left"),(2,"top_left")]
swarm_states = S.move(instructions)[0]
for state in swarm_states:
    print(state)

instructions = [(7,"top"),(9,"top_right")]
swarm_states = S.move(instructions)[0]
for state in swarm_states:
    print(state)

instructions = [(8,"left"),(9,"top")]
swarm_states = S.move(instructions)[0]
for state in swarm_states:
    print(state)
"""