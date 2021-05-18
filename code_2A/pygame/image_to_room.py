import pickle
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


def get_image(image_path):
    """Get a numpy array of an image so that one can access values[x][y]."""
    image = Image.open(image_path, "r")

    width, height = image.size
    pixel_values = list(image.getdata())
    if image.mode == "RGB":
        channels = 3
    elif image.mode == "L":
        channels = 1
    elif image.mode == "RGBA":
        channels = 4
    else:
        print("Unknown mode: %s" % image.mode)
        return None
    pixel_values = np.array(pixel_values).reshape((height, width, channels))
    
    return pixel_values


def SaveFile(image,image_name):
        
    file = open("./rooms/"+image_name, "wb")
    fileTable = np.zeros((128,220))

    for row in range(128):
        for col in range(220):
            if image[row][col][0] == 0 and image[row][col][1] == 0 and image[row][col][2] == 0:      # 0 pour un mur (noir)
                fileTable[row][col] = 0
            elif image[row][col][0] == 255 and image[row][col][1] == 0:  # 1 pour un mesureur (rouge)
                fileTable[row][col] = 1
            elif image[row][col][1] == 255 and image[row][col][0] == 0:  # 2 pour un mesureur (vert)
                fileTable[row][col] = 2
            elif image[row][col][2] == 255 and image[row][col][0] == 0:  # 3 pour un mesureur (bleu)
                fileTable[row][col] = 3
            else:                                                              # -1 pour rien du tout
                fileTable[row][col] = -1    

    fileTable = np.transpose(fileTable) 

    pickle.dump(fileTable, file)
    file.close()
        

image = get_image("./img/bouygues_room.png")
plt.imshow(image)
plt.show()
SaveFile(image,"bouygues.pickle")
