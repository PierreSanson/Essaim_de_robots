import numpy as np

# https://stackoverflow.com/questions/34438313/identifying-groups-of-similar-numbers-in-a-list
def ordered_cluster(data, max_diff):
    current_group = ()
    for item in data:
        test_group = current_group + (item, )
        test_group_mean = np.mean(test_group)
        if all((abs(test_group_mean - test_item) < max_diff for test_item in test_group)):
            current_group = test_group
        else:
            yield current_group
            current_group = (item, )
    if current_group:
        yield current_group


def find_index_walls(table):
    horizontal_index = []
    vertical_index  = []

    L = len(table)      # nombre de lignes
    C = len(table[0])   # nombre de colonnes

    # balayage horizontal
    outside_a_wall = True
    for l in range(L):
        for c in range(C):
            if outside_a_wall and table[l,c] == 0:
                outside_a_wall = False
                horizontal_index.append(c)
            
            if not outside_a_wall and table[l,c] == -1:
                outside_a_wall = True

    # balayage vertical
    outside_a_wall = True
    for c in range(C):
        for l in range(L):
            if outside_a_wall and table[l,c] == 0:
                outside_a_wall = False
                vertical_index.append(l)
            
            if not outside_a_wall and table[l,c] == -1:
                outside_a_wall = True  

    horizontal_index.sort()
    vertical_index.sort()

    return horizontal_index, vertical_index


def average_index_walls(horizontal_index, vertical_index):
    horizontal_clusters = ordered_cluster(horizontal_index,10)
    vertical_clusters = ordered_cluster(vertical_index,10)

    horizontal_averages = []
    vertical_averages = []
    for cluster in horizontal_clusters:
        horizontal_averages.append(np.floor(np.mean(cluster)))
    for cluster in vertical_clusters:
        vertical_averages.append(np.floor(np.mean(cluster)))

    return horizontal_averages, vertical_averages


def closest(index,ref):
    m, m_index = abs(index-int(ref[0])), 0
    for i in range(len(ref)):
        if abs(index-int(ref[i])) < m:
            m = abs(index-int(ref[i]))
            m_index = i

    return int(ref[m_index])


def nb_neighbours(liste):
    number = 0

    for element in liste :
        if element == 0:
            number += 1

    return number


def not_an_error(x,y,table):
    if table[x+1,y] == 0 and table[x+1,y+1] == 0 and table[x+1,y] == 0:
        neighbours_indexes = [(x-1,y+1),(x-1,y),(x,y-1),(x+1,y-1),(x+1,y+2),(x,y+2),(x+2,y),(x+2,y+1)]     
    elif table[x+1,y] == 0 and table[x+1,y-1] == 0 and table[x,y-1] == 0:
        neighbours_indexes = [(x-1,y-1),(x-1,y),(x,y+1),(x+1,y+1),(x,y-2),(x+1,y-2),(x+2,y),(x+2,y-1)]
    elif table[x-1,y] == 0 and table[x-1,y-1] == 0 and table[x,y-1] == 0:
        neighbours_indexes = [(x-1,y+1),(x,y+1),(x+1,y),(x+1,y-1),(x-2,y),(x-2,y-1),(x,y-2),(x-1,y-2)]
    elif table[x-1,y+1] == 0 and table[x,y+1] == 0 and table[x-1,y] == 0:
        neighbours_indexes = [(x-1,y-1),(x,y-1),(x+1,y),(x+1,y+1),(x,y+2),(x-1,y+2),(x-2,y),(x-2,y+1)]
    else:
        return False

    neighbours_values = []
    for index in neighbours_indexes:
        neighbours_values.append(table[index[0],index[1]])

    if nb_neighbours(neighbours_values) < 4:
        return False

    return True


def find_direction(x,y,table):
    

def clean_walls(table):

    left_to_visit = []

    L = len(table)      # nombre de lignes
    C = len(table[0])   # nombre de colonnes

    for l in range(L):
        for c in range(C):
            if table[l,c] == 0:
                left_to_visit.append((l,c))

    while len(left_to_visit) > 0:
        (x,y) = left_to_visit.pop()
        if not not_an_error(x,y,table): # oh que c'est vilain
            table[x,y] = -1      

    return table


def straighten_walls(table):

    horizontal_index, vertical_index = find_index_walls(table)
    horizontal_averages, vertical_averages = average_index_walls(horizontal_index, vertical_index)

    L = len(table)      # nombre de lignes
    C = len(table[0])   # nombre de colonnes

    result = np.zeros((L,C))
    result = result -1
    
    # balayage horizontal
    outside_a_wall = True
    for l in range(L):
        for c in range(C):
            if outside_a_wall and table[l,c] == 0:
                outside_a_wall = False
                h_index = closest(c,horizontal_averages)
                result[l,h_index], result[l,h_index+1] = 0, 0
            
            if not outside_a_wall and table[l,c] == -1:
                outside_a_wall = True

    # balayage vertical
    outside_a_wall = True
    for c in range(C):
        for l in range(L):
            if outside_a_wall and table[l,c] == 0:
                outside_a_wall = False
                v_index = closest(l,vertical_averages)
                result[v_index,c], result[v_index+1,c] = 0, 0
            
            if not outside_a_wall and table[l,c] == -1:
                outside_a_wall = True  

    # recopier les autre couleurs que le noir
    for l in range(L):
        for c in range(C):
            if table[l,c] !=0 and table[l,c] != -1:
                result[l,c] = table[l,c]   

    result = clean_walls(result)        
            
    return result