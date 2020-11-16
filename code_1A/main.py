from GUI import *
from simu import *
from swarm import *
from tkinter import *
from tkinter import font
from tkinter.messagebox import *


class TkinterApp:
 
    def __init__(self):
        # fenêtre principale de l'application :
        self.swarm_size = 0
        self.swarm_shape = []
        self.objective = []
        self.objective_size = 0
        self.iter = 0
        self.root = Tk()
        self.root.title("Simulateur essaim de robots")
        self.underlined_font = font.Font(size=10, underline=True)  
        self.bold_font = font.Font(size=10, weight="bold")

        # bouton qui permet d'ouvrir la fenêtre pour configurer l'essaim de départ
        self.bt = Button(self.root, text="Choix de la configuration initiale", command=self.swarm_config)
        self.bt.grid(row=1, column=2)

        # bouton qui permet d'ouvrir la fenêtre pour configurer l'objectif
        self.bt = Button(self.root, text="Choix de l'objectif", command=self.objective_config)
        self.bt.grid(row=2, column=2)

        # choix du nombre d'itérations du programme
        self.l = Label(self.root,text="Nombre d'itérations", font=self.underlined_font)
        self.l.grid(row=0, column=0)

        self.s = Spinbox(self.root, from_=10, to=1000, increment=10)
        self.s.grid(row=1, column=0)

        # bouton radio pour choisir l'algorithme utilisé par la simulation
        self.l = Label(self.root, text="Algorithme de résolution", font=self.underlined_font)
        self.l.grid(row=3,column=0)

        self.radio_value = StringVar(value="v2")
        self.rb1 = Radiobutton(self.root, variable=self.radio_value, text="Clockwise", value="clockwise")
        self.rb2 = Radiobutton(self.root, variable=self.radio_value, text="v2", value="v2")
        self.rb1.grid(row=4,column=0)
        self.rb2.grid(row=5,column=0)


        # bouton pour lancer la simulation et afficher le résultat dans une nouvelle fenêtre
        self.bt = Button(self.root, text="Lancer la simulation", command=self.launch_simulation, font=self.bold_font)
        self.bt.grid(row=4, column=2)


        # petits espaces vides parce que c'est plus joli...
        self.horizontal_spacing = Label(self.root,text="          ")
        self.vertical_spacing = Label(self.root,text="   ")

        self.horizontal_spacing.grid(row=0,column=1)
        self.vertical_spacing.grid(row=2,column=0)


    def swarm_config(self):
        dialogue = Swarm_Configuration(self.root)
        self.root.wait_window(dialogue.top)


    def objective_config(self):
        dialogue = Objective_Configuration(self.root)
        self.root.wait_window(dialogue.top)


    def simulation(self):

        self.iter = int(self.s.get())
        self.method = self.radio_value.get()

        S = Swarm(self.swarm_size, self.swarm_shape)
        S.main_sequence(self.objective, self.iter, 100, 50, formation_method=self.method)

        return instructions_to_GUI(2*self.swarm_size,S,S.moves_sequence)


    def launch_simulation(self):
        if self.swarm_size != self.objective_size:
            showwarning("Erreur","L'essaim de départ et l'objectif ne comportent pas le même nombre de robots")
        else:
            # créer une nouvelle fenêtre en cliquant sur le bouton
            dialogue = Simulation(self.root)
            self.root.wait_window(dialogue.top)
            
        
class Swarm_Configuration:

    def __init__(self, parent):

        self.CB_state = 1
        top = self.top = Toplevel(parent)

        l = Label(top, text="Taille de la grille")
        l.grid(row=0,column=0)

        self.s = Spinbox(top, from_=1, to=10)
        self.s.grid(row=0, column=1)

        b = Button(top, text="Afficher la grille", command=self.display_grid)
        b.grid(row=0, column=2)


    def check_all(self):

        for val in self.CBs:
            val.set(self.CB_state)       
                
        self.CB_state = int(abs(self.CB_state-1))


    def display_grid(self):

        self.grid_size = int(self.s.get())
        self.CBs = [] #liste qui va contenir l'ensemble des valeurs associées aux check-buttons
        for ligne in range(self.grid_size):
            for colonne in range(self.grid_size):
                self.var = IntVar()
                self.cb = Checkbutton(self.top, variable = self.var)
                self.cb.grid(row=ligne, column=colonne+3)
                self.CBs.append(self.var)
        
        b = Button(self.top, text="Valider et fermer cette fenêtre", command=self.get_swarm_shape)
        b.grid(row=self.grid_size, column=2)

        bb = Button(self.top, text="Tout cocher/décocher", command=self.check_all)
        bb.grid(row=1, column=2)


    def get_swarm_shape(self): 

        shape = np.zeros((self.grid_size,self.grid_size))

        for ligne in range(self.grid_size):
            for colonne in range(self.grid_size):
                shape[ligne,colonne] = self.CBs[ligne*self.grid_size+colonne].get()

        if np.array_equal(shape,np.zeros((self.grid_size,self.grid_size))):
            shape = []
            size = 0
        else:   
            for k in range(int(self.grid_size/2)+1): # nettoyage de la matrice pour ne pas garder des colonnes vides
                shape = clean_shape(shape)

        if len(shape) != 0:
            compteur = 1 # attribution de leurs numéros aux robots
            for i in range(len(shape)):
                for j in range(len(shape[0])):
                    if shape[i,j] == 1:
                        shape[i,j] = compteur
                        compteur += 1
            size = compteur - 1

        app.swarm_size = size
        app.swarm_shape = shape

        self.top.destroy()


class Objective_Configuration:

    def __init__(self, parent):

        self.CB_state = 1
        top = self.top = Toplevel(parent)

        l = Label(top, text="Taille de la grille")
        l.grid(row=0,column=0)

        self.s = Spinbox(top, from_=1, to=10)
        self.s.grid(row=0, column=1)

        b = Button(top, text="Afficher la grille", command=self.display_grid)
        b.grid(row=0, column=2)


    def check_all(self):

        for val in self.CBs:
            val.set(self.CB_state)       
        
        self.CB_state = int(abs(self.CB_state-1))


    def display_grid(self):

        self.grid_size = int(self.s.get())
        self.CBs = [] #liste qui va contenir l'ensemble des valeurs associées aux check-buttons
        for ligne in range(self.grid_size):
            for colonne in range(self.grid_size):
                self.var = IntVar()
                self.cb = Checkbutton(self.top, variable = self.var)
                self.cb.grid(row=ligne, column=colonne+3)
                self.CBs.append(self.var)
        
        b = Button(self.top, text="Valider et fermer cette fenêtre", command=self.get_objective)
        b.grid(row=self.grid_size, column=2)

        bb = Button(self.top, text="Tout cocher/décocher", command=self.check_all)
        bb.grid(row=1, column=2)


    def get_objective(self): 

        shape = np.zeros((self.grid_size,self.grid_size))

        for ligne in range(self.grid_size):
            for colonne in range(self.grid_size):
                shape[ligne,colonne] = self.CBs[ligne*self.grid_size+colonne].get()
        
        if np.array_equal(shape,np.zeros((self.grid_size,self.grid_size))):
            shape = []
            size = 0
        else:   
            for k in range(int(self.grid_size/2)+1): # nettoyage de la matrice pour ne pas garder des colonnes vides
                shape = clean_shape(shape)

        if len(shape) != 0:
            compteur = 1 # attribution de leurs numéros aux robots
            for i in range(len(shape)):
                for j in range(len(shape[0])):
                    if shape[i,j] == 1:
                        compteur += 1
            size = compteur - 1

        app.objective = shape
        app.objective_size = size

        self.top.destroy()


class Simulation:

    def __init__(self, parent):

            top = self.top = Toplevel(parent)

            steps = app.simulation()
            grid = np.array([])

            disp = Display(top,600, 600, grid, steps)
            disp.canvas.pack()
            top.bind('<Left>', disp.leftKey)
            top.bind('<Right>', disp.rightKey)
            disp.disp_init()

        
# programme principal
if __name__ == '__main__':
     
    app = TkinterApp()
    app.root.mainloop()