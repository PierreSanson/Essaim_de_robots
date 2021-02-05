####################################################################
# CREDITS :
# Pyint by Burak
# 3.09.2019
#
# pyint.py file (MAIN PROGRAM)
# Original purpose :  A 64x64 pixel painter program made in python pygame
####################################################################

# besoins du programme de base
import pygame as pg
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
import sys

# mes besoins
import numpy as np
import pickle
from clean_draw import straighten_walls, clean_walls
from scipy import ndimage, misc


sys.setrecursionlimit(10000)
pg.init()

sw, sh = 1551, 854
sc = (sw//2, sh//2)
screen = pg.display.set_mode((sw, sh))
pg.display.set_caption("Initial configuration")


brushImage = pg.transform.scale(pg.image.load('./img/brush.jpg'), (25,25))
eraserImage = pg.transform.scale(pg.image.load('./img/eraser.jpg'), (25,25))
trashImage = pg.transform.scale(pg.image.load('./img/trash.jpg'), (25,25))


def Remap(oldlow, oldhigh, newlow, newhigh, value):
    oldRange = (oldhigh - oldlow)
    newRange = (newhigh - newlow)
    newVal = (((value - oldlow) * newRange) / oldRange) + newlow
    return newVal


def draw_walls():
    wall_color = (50,50,50)
    wall_thickness = 4

    pg.draw.rect(screen, (150,150,150), (g1.xCount * g1.cellSize, 0, sw - g1.xCount * g1.cellSize, g1.yCount*g1.cellSize))
    pg.draw.rect(screen, (80,80,80), (0, g1.xCount * g1.cellSize, sw, sh-g1.yCount*g1.cellSize))

    pg.draw.rect(screen, wall_color, (g1.xCount * g1.cellSize, 0, wall_thickness, g1.yCount*g1.cellSize))
    pg.draw.rect(screen, wall_color, (0, g1.yCount*g1.cellSize-wall_thickness, sw, wall_thickness))

    pg.draw.rect(screen, wall_color, (0, 0, sw, wall_thickness))
    pg.draw.rect(screen, wall_color, (sw-wall_thickness, 0, wall_thickness, sh))
    pg.draw.rect(screen, wall_color, (0, 0, wall_thickness, sh))
    pg.draw.rect(screen, wall_color, (0, sh - wall_thickness, sw, wall_thickness))


class Cell(object):

    def __init__(self, size, color=[0, 0, 0]):
        self.size = size
        self.color = color
        self.subsurface = pg.Surface((self.size,self.size))
        self.subsurface.fill(self.color)
        self.pos = (0, 0)

    def change_color(self, color):
        self.color = color
        self.subsurface.fill(self.color)

    def Draw(self, win, x, y):
        self.pos = (x, y)
        win.blit(self.subsurface, self.pos)


class Grid(object):
    def __init__(self, xc, yc, csize, x, y, color=[255, 255, 255]):
        self.xCount = xc
        self.yCount = yc
        self.cellSize = csize
        self.pos = (x, y)
        self.color = color
        self.grid = []
        
        for row in range(self.yCount):
            self.grid.append([])
            for column in range(self.xCount):
                self.grid[row].append(Cell(self.cellSize, self.color))
       
    def Draw(self, win):
        for row in range(self.yCount):
            for column in range(self.xCount):
                self.grid[row][column].Draw(win, self.pos[0]+(self.cellSize*column), self.pos[1]+(self.cellSize*row))

    def change_color(self, posy, posx, color):
        self.grid[posy][posx].change_color(color)

    def clean(self):
        for row in range(self.yCount):
            for column in range(self.xCount):
                self.grid[row][column].change_color(self.color)



class Button(object):
    active = False
    clicked = False
    rollOver = False

    def __init__(self, posX, posY, width, height, color, text="Button", type=1, fontSize=25, fontColor=(0, 0, 0)):
        self.pos = [posX, posY]
        self.drawPos = self.pos.copy()
        self.width, self.height = width, height
        self.color = color
        self.text, self.fontSize, self.fontColor = text, fontSize, fontColor
        self.type = type
        self.subsurface = pg.Surface((self.width, self.height))
        self.subsurface.fill(self.color)
        self.font = pg.font.SysFont(None, self.fontSize)
        self.mes = self.font.render(self.text, True, self.fontColor)
        self.slideVal = 0

    def Draw(self, win, val=-1):
        if self.type == 1:
            if self.rollOver and not self.clicked:
                self.subsurface.set_alpha(255)
            else:
                self.subsurface.set_alpha(200)
            
            win.blit(self.subsurface, self.pos)
            self.subsurface.blit(self.mes, (15, self.height/3))

        elif self.type == 2:
            self.slideVal = Remap(-60,60,1,3,(self.pos[0]- self.drawPos[0]))
            pg.draw.rect(screen, (200,200,200), (self.drawPos[0]-100, self.drawPos[1]-30, 168, 60))
            pg.draw.rect(screen, (140,140,140), (self.drawPos[0]-60, self.drawPos[1]+self.height/3, 120, self.height/2))
            pg.draw.rect(screen, (220,220,220), (self.drawPos[0]-90, self.drawPos[1]+1, 20, 20))
            self.valMes = self.font.render(str(val), True, (30,30,30))
            win.blit(self.valMes, (self.drawPos[0]-85, self.drawPos[1]+3))
            win.blit(self.subsurface, (self.pos[0]-self.width/2, self.pos[1]))
            win.blit(self.mes, (self.drawPos[0]-90, self.drawPos[1]-25))

colors = [ [0, 0, 0], [255,0,0], [0,255,0], [0,0,255] ]
colorCells = []

for color in colors:
    colorCells.append(Cell(20, color))

colorTitleFont = pg.font.SysFont(None, 25)
colorTitle = colorTitleFont.render("Color Palette", True, (50,50,50))
g1 = Grid(220, 128, 6, 0, 0)
save_b = Button(20,790,85,40, (200, 200, 200), "S a v e", 1)
load_b = Button(120,790,85,40, (200, 200, 200), "L o a d", 1)
straighten_b  = Button(220,790,160,40, (200, 200, 200), "S t r a i g h t e n", 1)
clean_b = Button(400,790,95,40, (200, 200, 200), "C l e a n", 1)
SL_Buttons = [save_b, load_b, straighten_b, clean_b]

S_brushSize = Button(1450, 305, 10,20, (240,240,240), "Brush Size", 2)
S_eraserSize = Button(1450, 225, 10,20, (240,240,240), "Eraser Size", 2)
S_buttons = [S_brushSize, S_eraserSize]

B_penTool = Button(1395, 60, 30, 30, (80,80,80), "", 1)
B_eraserTool = Button(1445, 60, 30, 30, (80,80,80), "", 1)
B_trash = Button(1420, 110, 30, 30, (80,80,80), "", 1)
B_Buttons = [B_penTool, B_eraserTool, B_trash]

fileFont = pg.font.SysFont(None, 30)
nameSurface = pg.Surface((370,40))
nameSurface.fill(pg.Color((200,200,200)))
fileName = "unnamed"

selectedTool = 0
selectedToolBefore = 0

colorUsing = [0, 0, 0]
selectedColor = [0,0,0]
clicking = False
penSize = 3
eraserSize = 3

round = -1
clock = pg.time.Clock()
holdingCTRL = False
mouseRelPosX = 0
mouseRelPosY = 0

positions = [(1357, 406), (1382, 406), (1407, 406), (1432, 406)]

def draw_palette():

    global positions

    screen.blit(colorTitle, (1350, 380))
    pg.draw.rect(screen, (200, 200, 200), (1350, 400, 170, 75))

    for i, color in enumerate(colorCells):
        screen.blit(color.subsurface, positions[i])

    pg.draw.rect(screen, (235, 235, 235), (positions[-1][0] +44, positions[-1][1] + 27, 35, 35))
    pg.draw.rect(screen, colorUsing, (positions[-1][0] +50, positions[-1][1] + 33, 23, 23))


def paint(var):
    global mouseRelPosX, mouseRelPosY
    if var == 0:
        sizeToDraw = penSize
    elif var == 1:
        sizeToDraw = eraserSize

    if sizeToDraw == 1:
        mouseRelPosY = max(penSize - 1, min(g1.yCount - 1, int(Remap(0, (g1.cellSize * g1.yCount), 0, g1.yCount, pg.mouse.get_pos()[1]))))
        mouseRelPosX = max(penSize - 1, min(g1.xCount - 1, int(Remap(0, (g1.cellSize * g1.xCount), 0, g1.xCount, pg.mouse.get_pos()[0]))))
        g1.change_color(mouseRelPosY, mouseRelPosX, colorUsing)

    if sizeToDraw == 2:
        mouseRelPosY = max(penSize - 2, min(g1.yCount - 2, int(Remap(0, (g1.cellSize * g1.yCount), 0, g1.yCount, pg.mouse.get_pos()[1]))))
        mouseRelPosX = max(penSize - 2, min(g1.xCount - 2, int(Remap(0, (g1.cellSize * g1.xCount), 0, g1.xCount, pg.mouse.get_pos()[0]))))
        g1.change_color(mouseRelPosY, mouseRelPosX, colorUsing)
        g1.change_color(mouseRelPosY - 1, mouseRelPosX, colorUsing)
        g1.change_color(mouseRelPosY, mouseRelPosX - 1, colorUsing)
        g1.change_color(mouseRelPosY, mouseRelPosX + 1, colorUsing)
        g1.change_color(mouseRelPosY + 1, mouseRelPosX, colorUsing)
        g1.change_color(mouseRelPosY + 1, mouseRelPosX + 1, colorUsing)
        g1.change_color(mouseRelPosY - 1, mouseRelPosX - 1, colorUsing)
        g1.change_color(mouseRelPosY - 1, mouseRelPosX + 1, colorUsing)
        g1.change_color(mouseRelPosY + 1, mouseRelPosX - 1, colorUsing)
    
    if sizeToDraw == 3:
        mouseRelPosY = max(penSize - 3, min(g1.yCount - 3, int(Remap(0, (g1.cellSize * g1.yCount), 0, g1.yCount, pg.mouse.get_pos()[1]))))
        mouseRelPosX = max(penSize - 3, min(g1.xCount - 3, int(Remap(0, (g1.cellSize * g1.xCount), 0, g1.xCount, pg.mouse.get_pos()[0]))))
        g1.change_color(mouseRelPosY, mouseRelPosX, colorUsing)
        g1.change_color(mouseRelPosY - 1, mouseRelPosX, colorUsing)
        g1.change_color(mouseRelPosY, mouseRelPosX - 1, colorUsing)
        g1.change_color(mouseRelPosY, mouseRelPosX + 1, colorUsing)
        g1.change_color(mouseRelPosY + 1, mouseRelPosX, colorUsing)
        g1.change_color(mouseRelPosY + 1, mouseRelPosX + 1, colorUsing)
        g1.change_color(mouseRelPosY - 1, mouseRelPosX - 1, colorUsing)
        g1.change_color(mouseRelPosY - 1, mouseRelPosX + 1, colorUsing)
        g1.change_color(mouseRelPosY + 1, mouseRelPosX - 1, colorUsing)
        g1.change_color(mouseRelPosY, mouseRelPosX - 2, colorUsing)
        g1.change_color(mouseRelPosY + 1, mouseRelPosX - 2, colorUsing)
        g1.change_color(mouseRelPosY + 2, mouseRelPosX - 2, colorUsing)
        g1.change_color(mouseRelPosY - 1, mouseRelPosX - 2, colorUsing)
        g1.change_color(mouseRelPosY - 2, mouseRelPosX - 2, colorUsing)
        g1.change_color(mouseRelPosY, mouseRelPosX + 2, colorUsing)
        g1.change_color(mouseRelPosY + 1, mouseRelPosX + 2, colorUsing)
        g1.change_color(mouseRelPosY + 2, mouseRelPosX + 2, colorUsing)
        g1.change_color(mouseRelPosY - 1, mouseRelPosX + 2, colorUsing)
        g1.change_color(mouseRelPosY - 2, mouseRelPosX + 2, colorUsing)
        g1.change_color(mouseRelPosY + 2, mouseRelPosX, colorUsing)
        g1.change_color(mouseRelPosY + 2, mouseRelPosX - 1, colorUsing)
        g1.change_color(mouseRelPosY + 2, mouseRelPosX + 1, colorUsing)
        g1.change_color(mouseRelPosY - 2, mouseRelPosX, colorUsing)
        g1.change_color(mouseRelPosY - 2, mouseRelPosX - 1, colorUsing)
        g1.change_color(mouseRelPosY - 2, mouseRelPosX + 1, colorUsing)


def tool_activate(toolIndex):
    global colorUsing
    if toolIndex == 0:
        colorUsing = selectedColor.copy()
    if toolIndex == 1:
        colorUsing = g1.color.copy()


def FileManager(var):
    global fileExtension
    window = Tk()
    window.withdraw()
        
    availableFormats = [("Pickle dump", "*.pickle")]

    if var == 0:
        filename = askopenfilename(title="Open File", filetypes=availableFormats)
    elif var == 1:
        filename = asksaveasfilename(title="Save File", filetypes=availableFormats)

    if filename:
        name = filename[:]
        return name


def SaveFile(gridObject, filePath):
    global fileName

    if filePath:
        
        if len(filePath) >= 7:  # This just makes sure we have .pickle at the end of our file selection
            if filePath[-7:] != '.pickle':
                filePath = filePath + '.pickle'
        else:
            filePath = filePath + '.pickle'
        
        file = open(filePath, "wb")

        fileTable = np.zeros((128,220))

        for row in range(gridObject.yCount):
            for column in range(gridObject.xCount):
                if gridObject.grid[row][column].color[0] == 0 and gridObject.grid[row][column].color[1] == 0 and gridObject.grid[row][column].color[2] == 0:      # 0 pour un mur (noir)
                    fileTable[row][column] = 0
                elif gridObject.grid[row][column].color[0] == 255 and gridObject.grid[row][column].color[1] == 0:  # 1 pour un mesureur (rouge) ####### on y rentre dans tous les cas pour du blanc 
                    fileTable[row][column] = 1
                elif gridObject.grid[row][column].color[1] == 255 and gridObject.grid[row][column].color[0] == 0:  # 2 pour un mesureur (vert)
                    fileTable[row][column] = 2
                elif gridObject.grid[row][column].color[2] == 255 and gridObject.grid[row][column].color[0] == 0:  # 3 pour un mesureur (bleu)
                    fileTable[row][column] = 3
                else:                                               # -1 pour rien du tout
                    fileTable[row][column] = -1          

        pickle.dump(fileTable, file)
        file.close()

        filePathList = filePath.split("/")
        fileName = filePathList[-1]
        pg.display.set_caption("Initial configuration - " + fileName)


def OpenFile(filePath):
    global g1, fileName

    if filePath:
        file = open(filePath, "rb")
        colors = pickle.load(file)
        file.close()

        for row in range(g1.yCount):
            for column in range(g1.xCount):
                if colors[row][column] == 0:
                    g1.change_color(row,column,[0,0,0])
                elif colors[row][column] == 1:
                    g1.change_color(row,column,[255,0,0])
                elif colors[row][column] == 2:
                    g1.change_color(row,column,[0,255,0])
                elif colors[row][column] == 3:
                    g1.change_color(row,column,[0,0,255])
                else:
                    g1.change_color(row,column,[255,255,255])     
        
        filePathList = filePath.split("/")
        fileName = filePathList[-1]
        pg.display.set_caption("Initial configuration - " + fileName)


def Clean(gridObject):
    
    colors = np.zeros((128,220))

    for row in range(gridObject.yCount):
            for column in range(gridObject.xCount):
                if gridObject.grid[row][column].color[0] == 0 and gridObject.grid[row][column].color[1] == 0 and gridObject.grid[row][column].color[2] == 0:      # 0 pour un mur (noir)
                    colors[row][column] = 0
                elif gridObject.grid[row][column].color[0] == 255 and gridObject.grid[row][column].color[1] == 0:  # 1 pour un mesureur (rouge) ####### on y rentre dans tous les cas pour du blanc 
                    colors[row][column] = 1
                elif gridObject.grid[row][column].color[1] == 255 and gridObject.grid[row][column].color[0] == 0:  # 2 pour un mesureur (vert)
                    colors[row][column] = 2
                elif gridObject.grid[row][column].color[2] == 255 and gridObject.grid[row][column].color[0] == 0:  # 3 pour un mesureur (bleu)
                    colors[row][column] = 3
                else:                                               # -1 pour rien du tout
                    colors[row][column] = -1 

    colors = clean_walls(colors)

    for row in range(gridObject.yCount):
            for column in range(gridObject.xCount):
                if colors[row][column] == 0:
                    gridObject.change_color(row,column,[0,0,0])
                elif colors[row][column] == 1:
                    gridObject.change_color(row,column,[255,0,0])
                elif colors[row][column] == 2:
                    gridObject.change_color(row,column,[0,255,0])
                elif colors[row][column] == 3:
                    gridObject.change_color(row,column,[0,0,255])
                else:
                    gridObject.change_color(row,column,[255,255,255])     


def Straighten(gridObject):
    
    colors = np.zeros((128,220))

    for row in range(len(gridObject.grid)):
            for column in range(len(gridObject.grid[row])):
                if gridObject.grid[row][column].color[0] == 0 and gridObject.grid[row][column].color[1] == 0 and gridObject.grid[row][column].color[2] == 0:      # 0 pour un mur (noir)
                    colors[row][column] = 0
                elif gridObject.grid[row][column].color[0] == 255 and gridObject.grid[row][column].color[1] == 0:  # 1 pour un mesureur (rouge) ####### on y rentre dans tous les cas pour du blanc 
                    colors[row][column] = 1
                elif gridObject.grid[row][column].color[1] == 255 and gridObject.grid[row][column].color[0] == 0:  # 2 pour un mesureur (vert)
                    colors[row][column] = 2
                elif gridObject.grid[row][column].color[2] == 255 and gridObject.grid[row][column].color[0] == 0:  # 3 pour un mesureur (bleu)
                    colors[row][column] = 3
                else:                                               # -1 pour rien du tout
                    colors[row][column] = -1 

    while not np.equal(colors,straighten_walls(colors)).all():
        colors = straighten_walls(colors)

    for row in range(g1.yCount):
            for column in range(g1.xCount):
                if colors[row][column] == 0:
                    g1.change_color(row,column,[0,0,0])
                elif colors[row][column] == 1:
                    g1.change_color(row,column,[255,0,0])
                elif colors[row][column] == 2:
                    g1.change_color(row,column,[0,255,0])
                elif colors[row][column] == 3:
                    g1.change_color(row,column,[0,0,255])
                else:
                    g1.change_color(row,column,[255,255,255])    


def key_event_up(event):
    global penSize, holdingCTRL, selectedTool

    if event.key == pg.K_e:
        selectedTool = 1
        B_Buttons[1].clicked = True
        for subbutton in B_Buttons:
            if B_Buttons.index(subbutton) != selectedTool:
                subbutton.clicked = False
    elif event.key == pg.K_b:
        selectedTool = 0
        B_Buttons[0].clicked = True
        for subbutton in B_Buttons:
            if B_Buttons.index(subbutton) != selectedTool:
                subbutton.clicked = False

    if event.key == pg.K_s:
        if holdingCTRL:
            shortcutPath = FileManager(1)
            SaveFile(g1, shortcutPath)


while True:
    clock.tick(240)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()  ################################################################################################################################################################
            sys.exit()

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 3:
                selectedToolBefore = selectedTool
                selectedTool = 1
            elif event.button == 1:
                if pg.mouse.get_pos()[0] < g1.xCount*g1.cellSize and pg.mouse.get_pos()[1] < g1.yCount*g1.cellSize:
                    if selectedTool == 0 or selectedTool == 1:
                        paint(selectedTool)
                        clicking = True
                else:
                    for i, Scolor in enumerate(colorCells):
                        if Scolor.subsurface.get_rect(topleft=positions[i]).collidepoint(pg.mouse.get_pos()):
                            selectedColor = Scolor.color
                    for but in S_buttons:
                        if but.subsurface.get_rect(topleft=(but.pos[0]-but.width/2, but.pos[1])).collidepoint(pg.mouse.get_pos()):
                            but.active = True
                        else:
                            but.active = False
                    for i,but in enumerate(SL_Buttons):
                        if but.rollOver:
                            if i == 0:
                                cPath = FileManager(1)
                                SaveFile(g1, cPath)
                            elif i == 1:
                                cPath = FileManager(0)
                                OpenFile(cPath)
                            elif i == 2:
                                Straighten(g1)
                            elif i == 3:
                                Clean(g1)
                           
                    for but in B_Buttons:
                        if but.rollOver:
                            but.clicked = True

                            if B_Buttons.index(but) in [0, 1]:
                                selectedTool = B_Buttons.index(but)
                            else:
                                g1.clean()

                            for subbutton in B_Buttons:
                                if B_Buttons.index(subbutton) != selectedTool:
                                    subbutton.clicked = False
                    
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 3:
                selectedTool = selectedToolBefore
            elif event.button == 1:
                round *= -1
                clicking = False

                for but in S_buttons:
                    but.active = False

        if event.type == pg.MOUSEMOTION:
            if pg.mouse.get_pos()[0] < g1.xCount * g1.cellSize and pg.mouse.get_pos()[1] < g1.yCount * g1.cellSize:
                pg.mouse.set_visible(False)
            else:
                pass
                pg.mouse.set_visible(True)
            if clicking:
                if pg.mouse.get_pos()[0] < g1.xCount * g1.cellSize and pg.mouse.get_pos()[1] < g1.yCount * g1.cellSize:
                    paint(selectedTool)
            else:
                for but in SL_Buttons:
                    if but.subsurface.get_rect(topleft=but.pos).collidepoint(pg.mouse.get_pos()):
                        but.rollOver = True
                    else:
                        but.rollOver = False
                for but in B_Buttons:
                    if but.subsurface.get_rect(topleft=but.pos).collidepoint(pg.mouse.get_pos()):
                        but.rollOver = True
                    else:
                        but.rollOver = False
                for but in S_buttons:
                    if but.active:
                        but.pos[0] = max(but.drawPos[0]-60, min(pg.mouse.get_pos()[0], but.drawPos[0]+60))
                    else:
                        but.active = False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LCTRL:
                holdingCTRL = True

        if event.type == pg.KEYUP:
            key_event_up(event)

    tool_activate(selectedTool)

    screen.fill((255, 255, 255))
    g1.Draw(screen)
    draw_walls()
    
    for but in SL_Buttons:
        but.Draw(screen)

    screen.blit(colorTitleFont.render("Tools", True, (50,50,50)), (1350, 30))
    pg.draw.rect(screen, (200,200,200), (1350, 50, 170, 100))
    for but in B_Buttons:
        but.Draw(screen)

    screen.blit(colorTitleFont.render("Size Settings", True, (50, 50, 50)), (1350, 170))
    S_brushSize.Draw(screen, penSize)
    S_eraserSize.Draw(screen, eraserSize)
    penSize = int(S_brushSize.slideVal)
    eraserSize = int(S_eraserSize.slideVal)

    screen.blit(nameSurface, (600, 790))
    nameText = fileFont.render(fileName, True, (0, 0, 0))
    screen.blit(nameText, (610,sh-50))

    screen.blit(pg.transform.scale(eraserImage, (25,25)), (B_eraserTool.pos[0]+2, B_eraserTool.pos[1]+2))
    screen.blit(pg.transform.scale(brushImage, (25,25)), (B_penTool.pos[0]+2, B_penTool.pos[1]+2))
    screen.blit(pg.transform.scale(trashImage, (25,25)), (B_trash.pos[0]+2, B_trash.pos[1]+2))
    
    draw_palette()

    if selectedTool == 0:
        if pg.mouse.get_pos()[0] < g1.xCount * g1.cellSize and pg.mouse.get_pos()[1] < g1.yCount * g1.cellSize:
            pg.draw.circle(screen, colorUsing, (pg.mouse.get_pos()), penSize * 8, 1)
    elif selectedTool == 1:
        if pg.mouse.get_pos()[0] < g1.xCount * g1.cellSize and pg.mouse.get_pos()[1] < g1.yCount * g1.cellSize:
            pg.draw.circle(screen, (50,50,50), (pg.mouse.get_pos()), eraserSize * 8, 1)

    pg.display.update()