import pickle

filename = "test3"

pygamePath = "./results/"+filename+'-discrete-results.pickle'
noGUI_Path = "../noGUI/results/"+filename+'-noGUI-results.pickle'

file = open(pygamePath, "rb")
GUI_results = pickle.load(file)
file.close()

file = open(noGUI_Path, "rb")
noGUI_results = pickle.load(file)
file.close()

print(GUI_results.keys())
print(noGUI_results.keys())

print(GUI_results == noGUI_results)