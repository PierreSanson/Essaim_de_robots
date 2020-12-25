from sympy import Symbol
import numpy as np

def distObj(obj1, obj2):
    return np.sqrt((obj1.x-obj2.x)**2 + (obj1.y-obj2.y)**2) 

def distObjDict(obj1, dict2):
    return np.sqrt((obj1.x-dict2['x'])**2 + (obj1.y-dict2['y'])**2)

def distObjList(obj1, list2):
    return np.sqrt((obj1.x-list2[0])**2 + (obj1.y-list2[1])**2)

def circleLineInter(lineEmitter, obj, vel2D):
    r = obj.radius+lineEmitter.radius +5
    a = vel2D[0]
    b = -vel2D[1]
    c = -vel2D[0]*lineEmitter.y +vel2D[1]*lineEmitter.x

    x1 = obj.x
    y1 = obj.y

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

def signedAngle2Vects(vect1, vect2):
    vect1U = np.zeros(2)
    vect2U = np.zeros(2)
    if np.linalg.norm(vect1) !=0:
        vect1U = vect1/np.linalg.norm(vect1)
    if np.linalg.norm(vect2) !=0:
        vect2U = vect2/np.linalg.norm(vect2)
    dotV = np.dot(vect1U, vect2U)
    if dotV == 1 :
        return 0
    elif dotV == -1:
        return np.pi
    else:
        return (np.arctan2(vect2U[1], vect2U[0]) - np.arctan2(vect1U[1], vect1U[0]))

def signedAngle2Vects3(vect1, vect2):
    vect1U = np.zeros(2)
    vect2U = np.zeros(2)
    if np.linalg.norm(vect1) !=0:
        vect1U = vect1/np.linalg.norm(vect1)
    if np.linalg.norm(vect2) !=0:
        vect2U = vect2/np.linalg.norm(vect2)
    def length(v):
        return np.sqrt(v[0]**2+v[1]**2)
    def dot_product(v,w):
        return v[0]*w[0]+v[1]*w[1]
    def determinant(v,w):
        return v[0]*w[1]-v[1]*w[0]
    def inner_angle(v,w):
        dotV = dot_product(v,w)
        if dotV == 1 :
            print('dotV 1')
            return 0
        elif dotV == -1:
            print('dotV -1')
            return np.pi
        cosx=dotV/(length(v)*length(w))
        rad=np.arccos(cosx) # in radians
        return rad
    
    inner=inner_angle(vect1U,vect2U)
    if inner == 0 :
        return 0
    elif inner == np.pi:
        return np.pi
    det = determinant(vect1U,vect2U)
    if det<0: #this is a property of the det. If the det < 0 then B is clockwise of A
        return inner
    else: # if the det > 0 then A is immediately clockwise of B
        return 2*np.pi-inner
    

def signedAngle2Vects2(vect1, vect2):
    angle = np.arctan2( vect1[0]*vect2[1] -vect1[1]*vect2[0], vect1[0]*vect2[0] + vect1[1]*vect2[1])
    return angle

def rotate(vect, theta):
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    return np.dot(R, vect.T)
