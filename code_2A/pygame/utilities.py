import numpy as np
import pygame


def distSegments(seg1,seg2):
    minDist = np.sqrt((seg1[0][0]-seg2[0][0])**2 + (seg1[0][1]-seg2[0][1])**2)
    points = (0,0)
    dist2 = np.sqrt((seg1[1][0]-seg2[0][0])**2 + (seg1[1][1]-seg2[0][1])**2)
    dist3 = np.sqrt((seg1[1][0]-seg2[1][0])**2 + (seg1[1][1]-seg2[1][1])**2)
    dist4 = np.sqrt((seg1[0][0]-seg2[1][0])**2 + (seg1[0][1]-seg2[1][1])**2)

    if dist2 < minDist:
        minDist = dist2
        points = (1,0)
    elif dist3 < minDist:
        minDist = dist3
        points = (1,1)
    elif dist4 < minDist:
        minDist = dist4
        points = (0,1)

    return [minDist, points]

def distObj(obj1, obj2):
    return np.sqrt((obj1.x-obj2.x)**2 + (obj1.y-obj2.y)**2) 

def distObjDict(obj1, dict2):
    return np.sqrt((obj1.x-dict2['x'])**2 + (obj1.y-dict2['y'])**2)

def distObjList(obj1, list2):
    return np.sqrt((obj1.x-list2[0])**2 + (obj1.y-list2[1])**2)

def distLists(list1, list2):
    return np.sqrt((list1[0]-list2[0])**2 + (list1[1]-list2[1])**2)

def circleLineInter(lineEmitter, obj, vel2D, objDict = False, objRadius = 0):
    r = 0
    a = vel2D[0]
    b = -vel2D[1]
    c = -vel2D[0]*lineEmitter.y +vel2D[1]*lineEmitter.x
    if objDict:
        x1 = obj['x']
        y1 = obj['y']
        r = objRadius
    else:
        x1 = obj.x
        y1 = obj.y
        r = obj.radius+lineEmitter.radius + lineEmitter.margin

    dictSol = []

    if a != 0:
        a1 = 1 + (b/a)**2
        b1 = -2*x1 + 2*(b/a)*(c/a + y1)
        c1 = (c/a + y1)**2 +x1**2 - r**2

        delta = b1 ** 2 - 4*a1*c1
        xSols = []
        ySols = []
        
        if delta >=0:
            xSols = [(-b1-np.sqrt(delta))/(2*a1), (-b1+np.sqrt(delta))/(2*a1)]
            ySols = [((-b/a)*xSol -c/a) for xSol in xSols]
        
            for i in range(len(xSols)):
                dictSol.append({'x' : xSols[i], 'y' : ySols[i]})

    elif b !=0 :


        a1 = 1
        b1 = -2*y1
        c1 = (c/b)**2 +2*x1*c/b + x1**2 + y1**2 - r**2

        delta = b1 ** 2 - 4*a1*c1
        xSols = []
        ySols = []

        if delta >=0:
            ySols = [(-b1-np.sqrt(delta))/(2*a1), (-b1+np.sqrt(delta))/(2*a1)]
            xSols = [-c/b, -c/b]
        
            for i in range(len(xSols)):
                dictSol.append({'x' : xSols[i], 'y' : ySols[i]})
    

    return dictSol

def polygonLineInter(lineEmitter, polygon, barycenterPolygon, vel2D, win=None):
    a = vel2D[1]
    b = -vel2D[0]
    c = -b*lineEmitter.y -a*lineEmitter.x
    
    sols = []
    for i in range(len(polygon)):
        x, y = 0, 0
        xP, yP = 0,0
        vectLine = np.array([polygon[(i+1)%len(polygon)][0] - polygon[i][0], polygon[(i+1)%len(polygon)][1] - polygon[i][1]])
        lenLine = np.linalg.norm(vectLine)
        aL = vectLine[1]
        bL = -vectLine[0]
        cL = - bL*polygon[i][1] -aL*polygon[i][0]

        aP = bL
        bP = -aL
        cP = -bP*lineEmitter.y -aP*lineEmitter.x

        if b != 0 and aL*b - a*bL != 0:
            x = (-cL*b + bL*c)/(aL*b-a*bL)
            y = (-c-a*x)/b

        elif b == 0 and bL != 0 and a!=0:
            x = -c/a
            y = -cL/bL + aL*c/(bL*a)
        elif bL == 0 and b != 0 and aL!=0 :
            x = -cL/aL
            y = -c/b + a*cL/(b*aL)
        elif aL*b -a*bL == 0:
            x = polygon[i][0]
            y = polygon[i][1]
        vectCol = np.array([x - polygon[i][0], y - polygon[i][1]])

        if bP != 0 and aL*bP - aP*bL != 0:
            xP = (-cL*bP + bL*cP)/(aL*bP-aP*bL)
            yP = (-cP-aP*xP)/bP

        elif bP == 0 and bL != 0 and aP!=0:
            xP = -cP/aP
            yP = -cL/bL + aL*cP/(bL*aP)
        elif bL == 0 and bP != 0 and aL!=0 :
            xP = -cL/aL
            yP = -cP/bP + aP*cL/(bP*aL)
        elif aL*bP -aP*bL == 0:
            xP = lineEmitter.x
            yP = lineEmitter.y

        vectP = np.array([xP - lineEmitter.x, yP - lineEmitter.y])
        vectP2 = np.array([xP - polygon[i][0], yP - polygon[i][1]])

        angleCheck = signedAngle2Vects2([barycenterPolygon['x'] - lineEmitter.x ,barycenterPolygon['y'] - lineEmitter.y], vectP)


        if np.linalg.norm(vectP)<= lineEmitter.radius + 5.5 and np.linalg.norm(vectP2) <= lenLine and (np.dot(vectLine, vectP2) >= 0) :
            if abs(angleCheck)<=np.pi/2:
                # if win != None :
                    # pygame.draw.line(win, (255,0,255), (lineEmitter.x, lineEmitter.y), (lineEmitter.x + vectP[0], lineEmitter.y + vectP[1]), 3)
                    # pygame.draw.line(win, (255,0,255), (lineEmitter.x, lineEmitter.y), (barycenterPolygon['x'], barycenterPolygon['y']+ vectP[1]), 3)
                angleP = signedAngle2Vects2(vectP, vectLine)
                if angleP >= 0:
                    return ['indirect']
                else:
                    return ['direct']
        elif np.linalg.norm(vectCol) <= lenLine and (np.dot(vectLine, vectCol)) >= 0 :
            sols.append([x, y])
    return sols



def signedAngle2Vects2(vect1, vect2):
    angle = np.arctan2( vect1[0]*vect2[1] -vect1[1]*vect2[0], vect1[0]*vect2[0] + vect1[1]*vect2[1])
    return angle

def rotate(vect, theta):
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    return np.dot(R, vect.T)

def createPolygonMask(center, sides, radius):
    points = []
    x,y = center[0], center[1]
    theta = 2*np.pi/sides
    d = radius/np.cos(theta/2)
    vertexVect = np.array([0, 1])*d
    for i in range(sides):    
        vertexVect = rotate(vertexVect, theta)
        points.append([vertexVect[0]+x, vertexVect[1]+y])
    return points

def pointInPolygon(lineEmitter, polygon):
    inter = polygonLineInter(lineEmitter, polygon, {'x' : 0, 'y' : 0}, lineEmitter.vel2D)
    if len(inter) == 2:
        if np.dot(np.array([lineEmitter.x - inter[0][0], lineEmitter.y - inter[0][1]]), np.array([lineEmitter.x - inter[1][0], lineEmitter.y - inter[1][1]])) < 0 :
            return True
    return False