import numpy as np
from copy import deepcopy

def old_straighten_walls(table):
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
                result[l,c], result[l,c+1] = 0, 0
            
            if not outside_a_wall and table[l,c] == -1:
                outside_a_wall = True

    # balayage vertical
    outside_a_wall = True
    for c in range(C):
        for l in range(L):
            if outside_a_wall and table[l,c] == 0:
                outside_a_wall = False
                result[l,c], result[l+1,c] = 0, 0
            
            if not outside_a_wall and table[l,c] == -1:
                outside_a_wall = True  

    # recopier les autre couleurs que le noir
    for l in range(L):
        for c in range(C):
            if table[l,c] !=0 and table[l,c] != -1:
                result[l,c] = table[l,c]           
            
    return result

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
    m, m_index = abs(index-ref[0])
    for i in range(len(ref)):
        if abs(index-ref[i]) < m:
            m = abs(index-ref)
            m_index = i

    return ref[m_index]

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
            
    return result

# L= np.array([[1,2],[3,4]])
# print(L[0,1])