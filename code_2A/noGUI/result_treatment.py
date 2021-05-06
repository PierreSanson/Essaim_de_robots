import os
import pickle
import matplotlib.pyplot as plt

def LoadFile(filePath):

    if filePath:
        file = open(filePath, "rb")
        content = pickle.load(file)
        file.close()

        return content
    
    return None

def assemble_results_from_folder(folderPath):

    results = []
    if folderPath:
        for filename in os.listdir(folderPath):
            results.append(LoadFile(os.path.join(folderPath,filename)))
    
    result = {}
    
    # clés pour lesquelles les valeurs changent d'une simulation à l'autre
    var_keys = ['sim_number','start_pos','start_angle','measuredTile','pathLength','visitsPerTile','history','sim_duration']
    # clés pour lesquelles la valeur est toujours identique
    const_keys = ['nbRefPointBots','nbMeasurerBots','mb_exp_method','rpb_exp_method','rpb_sel_method','first_loop','surface']

    for key in var_keys:
        result[key] = []

    for key in const_keys:
        result[key] = results[0][key]

    for res in results:
        for key in res.keys():
            if key in var_keys:
                result[key].append(res[key])

    return results
    
test = assemble_results_from_folder("./results")


def heatmap(results):
    pass