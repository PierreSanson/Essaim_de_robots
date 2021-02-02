from bot import Bot

class ExplorerBot(Bot):

    def __init__(self, x, y, radius, room, objective, randomObjective = False, randomInterval = 10, color = (0,255,0), haveObjective = True, radiusDetection = 200, showDetails = False, message = "ExplorerBot",):
        super(self.__class__, self).__init__(x, y, radius, room, objective, randomObjective = randomObjective, randomInterval = randomInterval, color = color, haveObjective = haveObjective, radiusDetection = radiusDetection, showDetails = showDetails)
        self.message = message

    def show_self(self):
        print(self.message)