import obstacle as obs
from refPointBot import RefPointBot
from utilities import distObj, placeObstaclesOnLine


class Wall():
    def __init__(self, corners):

        self.obstacles = []
        self.obstacles_seen = []
        self.Xs = []
        self.Ys = []
        
        orientation = corners.pop()
        self.orientation = orientation
        self.corners = corners
        
        self.x_start = corners[0][1] # on fait bien attention entre x et y au sens d'un graphe Vs row et col pour numpy
        self.y_start = corners[0][0]


        ### ATTENTION : A CE MOMENT, LES COINS SONT ENCORE AU FORMAT  (ROW,COL)
        if orientation == 'v':
            self.width = corners[1][1] - corners[0][1]
            self.height = corners[3][0] - corners[0][0]

            # lignes:
            X = list(range(corners[0][1], corners[1][1],10))
            if not corners[1][1] in X:
                X.append(corners[1][1])
                
            # colonnes:
            Y = list(range(corners[0][0], corners[2][0],10))
            if not corners[2][0] in Y:
                Y.append(corners[2][0])


        elif orientation == 'h':
            self.width = corners[3][1] - corners[0][1]
            self.height = corners[1][0] - corners[0][0]

            # lignes:
            X = list(range(corners[0][1], corners[2][1],10))
            if not corners[2][1] in X:
                X.append(corners[2][1])
                
            # colonnes:
            Y = list(range(corners[0][0], corners[1][0],10))
            if not corners[1][0] in Y:
                Y.append(corners[1][0])

        ### UNE FOIS LE TRAITEMENT EFFECTUE, ON REVIENT AU FORMAT (X,Y)
        for corner in self.corners:
            corner.reverse()

        self.saveObstaclesMainCoord()


    def visibleForBot(self,bot):
        if (min(self.Xs) - bot.radiusDetection <= bot.x <= max(self.Xs) + bot.radiusDetection) and (min(self.Ys) - bot.radiusDetection <= bot.y <= max(self.Ys) + bot.radiusDetection):
            return True
        return False

    def visibleForBotUWB(self,bot):
        if (min(self.Xs) - bot.UWBradius <= bot.x <= max(self.Xs) + bot.UWBradius) and (min(self.Ys) - bot.UWBradius <= bot.y <= max(self.Ys) + bot.UWBradius):
            return True
        return False
 

    def saveObstaclesMainCoord(self):
        # on cherche toutes les coordonnées uniques
        tempXs = []
        tempYs = []
    
        for corner in self.corners:
            x = corner[0]
            y = corner[1]

            if not x in tempXs:
                tempXs.append(x)

            if not y in tempYs:
                tempYs.append(y)

        self.Xs = [min(tempXs),max(tempXs)]
        self.Ys = [min(tempYs),max(tempYs)]
        


class Room():

    def __init__(self, walls_corners, width, height):

        self.walls = []
        self.defWalls(walls_corners)

        Xs, Ys = [], []
        for wall in self.walls:
            Xs += wall.Xs
            Ys += wall.Ys

        self.Xmin, self.Xmax, self.Ymin, self.Ymax = min(Xs), max(Xs), min(Ys), max(Ys)

        self.bots = []

        self.width = width
        self.height = height

        obstacles = self.defineObstaclesFromWalls()
        self.obstacles = obstacles

        self.objects = self.bots + self.obstacles


    def addBots(self,bots):
        self.bots += bots 
        self.objects += bots


    def removeRefPointBots(self): ### pas très élégant, mais je n'ai pas trouvé d'autre solution : attention à ne pas itérer sur une liste qu'one est en train de modifier
        old_bots = self.bots[:]
        self.bots = []
        for bot in old_bots:
            if not isinstance(bot,RefPointBot):
                self.bots.append(bot)
        old_objects = self.objects[:]
        self.objects = []
        for obj in old_objects:
            if not isinstance(obj,RefPointBot):
                self.objects.append(obj)


    def defWalls(self, walls_corners):
        for corners in walls_corners:
            self.walls.append(Wall(corners))

                    
    def defineObstaclesFromWalls(self):
        obstacles = []
        radiusObstacles = 6                 
        spaceBetweenObstaclesCenter = 18  # il ne faut pas que (spaceBetweenObstaclesCenter - 2*radiusObstacles) soit plus grand qu'un robot, sinon ils passent au travers des murs

        for wall in self.walls: 
            wall_obstacles = [] 

            top_line = [[wall.x_start, wall.y_start],[wall.x_start+wall.width-1, wall.y_start]]
            left_line = [[wall.x_start, wall.y_start],[wall.x_start, wall.y_start + wall.height-1]]
            right_line = [[wall.x_start + wall.width-1, wall.y_start],[wall.x_start + wall.width-1, wall.y_start + wall.height-1]]
            bot_line = [[wall.x_start, wall.y_start+wall.height-1],[wall.x_start+wall.width-1, wall.y_start + wall.height-1]]
            
            if wall.orientation == 'h':
                y1 = top_line[0][1]
                y2 = bot_line[0][1]
                for x in placeObstaclesOnLine(top_line[0][0],top_line[1][0],radiusObstacles,spaceBetweenObstaclesCenter):
                    wall_obstacles.append(obs.Obstacle(x, y1, radiusObstacles, self,isWall='x', spacing = spaceBetweenObstaclesCenter, positionInWall='top'))
                    wall_obstacles.append(obs.Obstacle(x, y2, radiusObstacles, self,isWall='x', spacing = spaceBetweenObstaclesCenter, positionInWall='bot'))

            elif wall.orientation == 'v':    
                x1 = left_line[0][0]
                x2 = right_line[0][0]
                for y in placeObstaclesOnLine(left_line[0][1],left_line[1][1],radiusObstacles,spaceBetweenObstaclesCenter):
                    wall_obstacles.append(obs.Obstacle(x1, y, radiusObstacles, self,isWall='y', spacing = spaceBetweenObstaclesCenter, positionInWall='left'))
                    wall_obstacles.append(obs.Obstacle(x2, y, radiusObstacles, self, isWall='y', spacing = spaceBetweenObstaclesCenter, positionInWall='right'))                 

            obstacles += wall_obstacles
            wall.obstacles = wall_obstacles
    
        return obstacles
