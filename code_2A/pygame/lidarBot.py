
import pygame

import numpy as np
from scipy.optimize import fsolve
from sympy.solvers import solve
from sympy import Symbol

class LidarBot():
    def __init__(self, x, y, radius, room):
        self.room = room
        self.x = x
        self.y = y
        self.radius = radius
        self.vel2D = [0,0]
        self.objective = [x + 250, y+250]
        self.radiusDetection = 30
        self.rotationSpeed = 10


    def draw(self, win):
        pygame.draw.circle(win, (0,255,0), (self.x, self.y), self.radius)

    def move(self):
        self.x += self.vel2D[0]
        self.y += self.vel2D[1]
    
    def dist(self, obj1, obj2):
        return np.sqrt((obj1.x-obj2.x)**2 + (obj1.y-obj2.y)**2) 

    def checkCollision(self):
        collision = {}
        for obj in self.room.objects:
            if self.dist(self, obj) <= self.radiusDetection:
                sols = self.circleLineInter(self, obj, self.vel2D)
                if len(sols)>0:
                    if len(sols)>1:
                        minDist = self.dist(self, sols[0])
                        minIndex = 0
                        for i in range(1, len(sols[1:])):
                            dist = self.dist(self, sols[i])
                            if dist < minDist:
                                minDist = dist
                                minIndex = i
                        
                        collision[obj] = sols[minIndex]
                    else:
                        collision[obj] = sols[0]
        return collision

                
    def circleLineInter(self, lineEmitter, obj, vel2D):
        x, y = (Symbol('x'), Symbol('y'))
        sol = solve([(x - obj.x)**2 + (y - obj.y)**2 - obj.radius**2, vel2D[0]*y -vel2D[1]*x +(-vel2D[0]*lineEmitter.y +vel2D[1]*lineEmitter.x)], dict=True)
        return sol


    
    def goToObjective(self):
        collision = self.checkCollision()
        if collision :
            init = True
            minDist = None
            minObj = None
            for obj in collision:
                if init : 
                    minDist = self.dist(self, collision[obj])
                    minObj = obj
                    init = False
                else :
                    dist = self.dist(self, collision[obj])
                    if dist < minDist:
                        minDist = dist
                        minObj = obj
        else :
            vel2D = [-(self.objective[1] - self.y), self.objective[0] - self.x]


class Obstacle():
    def __init__(self, x, y, radius, room):
        self.room = room
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, win):
        pygame.draw.circle(win, (100,100,100), (self.x, self.y), self.radius)
    