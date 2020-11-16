from tkinter import *
from simu import *

import math
import time
import numpy as np



class Display:
    def __init__(self, master, canvas_width, canvas_height, grid, steps):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.bord = 20
        self.grid_width = canvas_width - self.bord
        self.grid_height = canvas_height - self.bord

        self.canvas = Canvas(master, width=canvas_width, height=canvas_height)
        self.dt = 1/1
        self.grid = grid
        self.i = 0
        self.steps = steps

    def disp_grid(self):
        
        grid_shape = self.grid.shape
        spacing = min(self.grid_height/grid_shape[0], self.grid_width/grid_shape[1])
        if grid_shape[0]%2==0:        
            for i in range(int(grid_shape[0]/2)+1):
                self.canvas.create_line(self.canvas_width/2 - spacing*grid_shape[1]/2, self.canvas_height/2 + spacing*i, self.canvas_width/2 + spacing*grid_shape[1]/2, self.canvas_height/2 + spacing*i)
                self.canvas.create_line(self.canvas_width/2 - spacing*grid_shape[1]/2, self.canvas_height/2 - spacing*i, self.canvas_width/2 + spacing*grid_shape[1]/2, self.canvas_height/2 - spacing*i)

        else:
            for i in range(int((grid_shape[0]-1)/2)+1):
                self.canvas.create_line(self.canvas_width/2 - spacing*grid_shape[1]/2, self.canvas_height/2 + spacing*i + spacing/2, self.canvas_width/2 + spacing*grid_shape[1]/2, self.canvas_height/2 + spacing*i + spacing/2)
                self.canvas.create_line(self.canvas_width/2 - spacing*grid_shape[1]/2, self.canvas_height/2 - spacing*i - spacing/2, self.canvas_width/2 + spacing*grid_shape[1]/2, self.canvas_height/2 - spacing*i - spacing/2)

        if grid_shape[1]%2==0:        
            for i in range(int(grid_shape[1]/2)+1):
                self.canvas.create_line(self.canvas_width/2 + spacing*i, self.canvas_height/2 - spacing*grid_shape[0]/2, self.canvas_width/2 + spacing*i, self.canvas_height/2 + spacing*grid_shape[0]/2)
                self.canvas.create_line(self.canvas_width/2 - spacing*i, self.canvas_height/2 - spacing*grid_shape[0]/2, self.canvas_width/2 - spacing*i, self.canvas_height/2 + spacing*grid_shape[0]/2)

        else:
            for i in range(int((grid_shape[1]-1)/2)+1):
                self.canvas.create_line(self.canvas_width/2 + spacing*i + spacing/2, self.canvas_height/2 - spacing*grid_shape[0]/2, self.canvas_width/2 + spacing*i + spacing/2, self.canvas_height/2 + spacing*grid_shape[0]/2)
                self.canvas.create_line(self.canvas_width/2 - spacing*i - spacing/2, self.canvas_height/2 - spacing*grid_shape[0]/2, self.canvas_width/2 - spacing*i - spacing/2, self.canvas_height/2 + spacing*grid_shape[0]/2)
                
    def disp_pivot(self, pos):
        y, x = pos
        grid_shape = self.grid.shape
        spacing = min(self.grid_height/grid_shape[0], self.grid_width/grid_shape[1])
        size = spacing/8
        center = (0,0)
        if grid_shape[0]%2 == 0 and grid_shape[1]%2 == 0:
            center = (self.canvas_width/2 - spacing*(grid_shape[1]/2 - x), self.canvas_height/2 - spacing*(grid_shape[0]/2 - y))

        elif grid_shape[0]%2 == 1 and grid_shape[1]%2 == 1:
            center = (self.canvas_width/2 - spacing/2 -spacing*((grid_shape[1]-1)/2 - x), self.canvas_height/2 - spacing/2 - spacing*((grid_shape[0] -1)/2 - y))

        elif grid_shape[0]%2 == 1 and grid_shape[1]%2 == 0:
            center = (self.canvas_width/2 - spacing*(grid_shape[1]/2 - x), self.canvas_height/2 - spacing/2 - spacing*((grid_shape[0] -1)/2 - y))

        elif grid_shape[0]%2 == 0 and grid_shape[1]%2 == 1:
            center = (self.canvas_width/2 - spacing/2 -spacing*((grid_shape[1]-1)/2 - x), self.canvas_height/2 - spacing*(grid_shape[0]/2 - y))

        self.canvas.create_oval(center[0] - size/2, center[1] - size/2, center[0] + size/2, center[1] + size/2, outline="#f11",
        fill="#f11", width=2)

    def disp_robot(self, pos, rot = False):
        y, x = pos
        grid_shape = self.grid.shape
        spacing = min(self.grid_height/grid_shape[0], self.grid_width/grid_shape[1])
        size = spacing
        center = (0,0)
        if grid_shape[0]%2 == 0 and grid_shape[1]%2 == 0:
            center = (self.canvas_width/2 - spacing*(grid_shape[1]/2 - x), self.canvas_height/2 - spacing*(grid_shape[0]/2 - y))

        elif grid_shape[0]%2 == 1 and grid_shape[1]%2 == 1:
            center = (self.canvas_width/2 - spacing/2 -spacing*((grid_shape[1]-1)/2 - x), self.canvas_height/2 - spacing/2 - spacing*((grid_shape[0] -1)/2 - y))

        elif grid_shape[0]%2 == 1 and grid_shape[1]%2 == 0:
            center = (self.canvas_width/2 - spacing*(grid_shape[1]/2 - x), self.canvas_height/2 - spacing/2 - spacing*((grid_shape[0] -1)/2 - y))

        elif grid_shape[0]%2 == 0 and grid_shape[1]%2 == 1:
            center = (self.canvas_width/2 - spacing/2 -spacing*((grid_shape[1]-1)/2 - x), self.canvas_height/2 - spacing*(grid_shape[0]/2 - y))

        if not rot :
            self.canvas.create_rectangle(center[0], center[1], center[0] + size, center[1] + size, outline="#fff",
        fill="#111")
        else :
            self.canvas.create_rectangle(center[0], center[1], center[0] + size, center[1] + size, outline="#fff",
        fill="#f11")

    def disp_step(self, step): # à compléter avec la translation
        grid = step[0]
        instructions = step[1]
        red_robots = []
        disp_pivot = []
        for instruction in instructions:
            p_robot = None
            t_robot = None
            for i in range(grid.shape[0]):
                for j in range(grid.shape[1]):
                    if grid[i][j] == instruction[0]:
                        t_robot = (i, j)
                        red_robots.append((i,j))
                    if grid[i][j] == instruction[1]:
                        p_robot = (i, j)
            if isinstance(instruction[2], int):
                if p_robot[0] == t_robot[0] and p_robot[1] == t_robot[1]-1:
                    if instruction[2] == 1:
                        disp_pivot.append((t_robot[0], t_robot[1]))
                    else:
                        disp_pivot.append((t_robot[0]+1, t_robot[1]))
                if p_robot[0] == t_robot[0] and p_robot[1] == t_robot[1]+1:
                    if instruction[2] == 1:
                        disp_pivot.append((t_robot[0]+1, t_robot[1]+1))
                    else:
                        disp_pivot.append((t_robot[0], t_robot[1]+1))
                if p_robot[0] == t_robot[0]+1 and p_robot[1] == t_robot[1]:
                    if instruction[2] == 1:
                        disp_pivot.append((t_robot[0]+1, t_robot[1]))
                    else:
                        disp_pivot.append((t_robot[0]+1, t_robot[1]+1))
                if p_robot[0] == t_robot[0]-1 and p_robot[1] == t_robot[1]:
                    if instruction[2] == 1:
                        disp_pivot.append((t_robot[0], t_robot[1]+1))
                    else:
                        disp_pivot.append((t_robot[0], t_robot[1]))

                if p_robot[0] == t_robot[0] + 1 and p_robot[1] == t_robot[1]-1:
                    disp_pivot.append((t_robot[0]+1, t_robot[1]))
                if p_robot[0] == t_robot[0] + 1 and p_robot[1] == t_robot[1]+1:
                    disp_pivot.append((t_robot[0]+1, t_robot[1]+1))
                if p_robot[0] == t_robot[0] - 1 and p_robot[1] == t_robot[1]+1:
                    disp_pivot.append((t_robot[0], t_robot[1]+1))
                if p_robot[0] == t_robot[0] - 1 and p_robot[1] == t_robot[1]-1:
                    disp_pivot.append((t_robot[0], t_robot[1]))

            else:
                if instruction[2] == 'top':
                    if p_robot[0] == t_robot[0] and p_robot[1] == t_robot[1]-1:
                        disp_pivot.append((t_robot[0], t_robot[1]))
                    else:
                        disp_pivot.append((t_robot[0], t_robot[1]+1))
                if instruction[2] == 'bottom':
                    if p_robot[0] == t_robot[0] and p_robot[1] == t_robot[1]-1:
                        disp_pivot.append((t_robot[0]+1, t_robot[1]))
                    else:
                        disp_pivot.append((t_robot[0]+1, t_robot[1]+1))
                if instruction[2] == 'left':
                    if p_robot[0] == t_robot[0]-1 and p_robot[1] == t_robot[1]:
                        disp_pivot.append((t_robot[0], t_robot[1]))
                    else:
                        disp_pivot.append((t_robot[0]+1, t_robot[1]))
                if instruction[2] == 'right':
                    if p_robot[0] == t_robot[0]-1 and p_robot[1] == t_robot[1]:
                        disp_pivot.append((t_robot[0], t_robot[1]+1))
                    else:
                        disp_pivot.append((t_robot[0]+1, t_robot[1]+1))
                
    
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                if grid[i][j] != 0:
                    if (i, j) in red_robots :
                        self.disp_robot((i, j), rot = True)
                    else : 
                        self.disp_robot((i, j))
        for inst in disp_pivot:
            self.disp_pivot((inst[0], inst[1]))
        
    def disp_init(self):
        self.canvas.delete("all")
        self.grid = self.steps[0][0]
        self.disp_grid()
        self.disp_step(self.steps[0])


    def rightKey(self, event):
        if self.i < len(self.steps)-1:
            self.i+=1
            self.canvas.delete("all")
            self.grid = self.steps[self.i][0]
            self.disp_grid()
            self.disp_step(self.steps[self.i])

    def leftKey(self, event):
        if self.i > 0:
            self.i-=1
            self.canvas.delete("all")
            self.grid = self.steps[self.i][0]
            self.disp_grid()
            self.disp_step(self.steps[self.i])
        
"""       
if __name__ == "__main__":
    master = Tk()
    steps = test_GUI()
    grid = np.zeros((3,3))
    disp = Display(master,600, 600, grid, steps)
    disp.canvas.pack()
    master.bind('<Left>', disp.leftKey)
    master.bind('<Right>', disp.rightKey)
    disp.disp_init()
    mainloop()
"""