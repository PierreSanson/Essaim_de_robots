from swarm import Robot, Swarm
import numpy as np 

class Room:
    def __init__(self,size):
        self.size = size
        self.map = np.zeros((size,size))
        self.swarm = np.array([])
    
    def spawn(self,swarm):
        dim = np.shape(swarm.shape)
        vert = dim[0]
        vert_spawn = int(((self.size-vert)/2))
        hori = dim[1]
        hori_spawn = int(((self.size-hori)/2))
        self.map[vert_spawn:vert_spawn+vert,hori_spawn:hori_spawn+hori] = swarm.shape
        self.swarm = swarm 
        self.swarm.update_neighbours()
    
    def update_map(self,states,old_shape): # renvoie la ;liste maps contenant la nouvelle carte associé à chaque nouvel état de l'essaim dans states

        maps = []
        
        robot_fixe = self.swarm.find_fixe()
        coord_grid = np.where(self.map==robot_fixe) # coordonnées d'un point fixe de la transformation dans la grille
        i,j = coord_grid[0][0],coord_grid[1][0]

        for state in states :
            new_coord_swarm = np.where(state==robot_fixe)
            new_x,new_y = new_coord_swarm[0][0],new_coord_swarm[1][0]

            map = np.zeros((self.size,self.size))
            new_shape = state

            dimensions = np.shape(new_shape)
            vertical_size = dimensions[0]
            horizontal_size = dimensions[1]

            map[int(i-new_x):int(i+vertical_size-new_x),int(j-new_y):int(j+horizontal_size-new_y)] = new_shape
            maps.append(map)
        
        self.map = maps[-1]
        return maps

"""
R = Room(6)
S = Swarm(3)
R.spawn(S)
R.swarm.update_neighbours()
print(R.map)

R.update((2,1,1))
print(R.map)
"""

def instructions_to_GUI(room_size,swarm,liste_instructions): # liste_instructions est une liste de listes qui contient les groupes d'instructions devant être exécutées en même temps
    R = Room(room_size)
    R.spawn(swarm)

    GUI_instructions = [] # liste de la forme [[état0,[instructions0to1]], [état1,[instructions1to2]], ...]
    old_map = R.map

    for instructions in liste_instructions:
        
        old_shape = R.swarm.shape
        movement = swarm.move(instructions)
        states, translations, rotations = movement[0], movement[1], movement[2]
        maps = R.update_map(states,old_shape)
        R.swarm.reset_moved()
        

        if rotations == []:
            instruction_GUI = [old_map, translations]
            GUI_instructions.append(instruction_GUI)
        else:
            instruction_GUI1 = [old_map, translations + rotations]
            instruction_GUI2 = [maps[0],rotations]
            GUI_instructions.append(instruction_GUI1)
            GUI_instructions.append(instruction_GUI2)

        old_map = maps[-1]
       
    GUI_instructions.append([old_map,[]])
    return(GUI_instructions)

# test de instructions_to_GUI
def test_GUI():
    swarm = [[0, 10, 6, 5, 11, 4],
            [0, 3, 9, 1, 8, 7],
            [0, 0, 0, 0, 2, 0], 
            [0, 0, 0, 0, 0, 0]]
    swarm = np.array(swarm)
    shape = [[0, 0, 1, 1, 1],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 1, 1],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 1, 1]]
    shape = np.array(shape)

    S = Swarm(11,  swarm)
    S.main_sequence(shape, 100, 100, 50)
    print(S.moves_sequence)
    return instructions_to_GUI(6,S,S.moves_sequence)

# exemple ne fonctionnant pas

    # swarm = [[2, 10, 6, 5, 11, 0],
    #         [4, 3, 9, 1, 8, 7],
    #         [0, 0, 0, 0, 0, 0], 
    #         [0, 0, 0, 0, 0, 0]]
    # swarm = np.array(swarm)
    # shape = [[0, 0, 1, 1, 1],
    #         [0, 0, 1, 0, 0],
    #         [0, 0, 1, 1, 1],
    #         [0, 0, 1, 0, 0],
    #         [0, 0, 1, 1, 1]]

