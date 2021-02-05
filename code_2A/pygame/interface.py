import pygame, pygame_menu

from main import Room, demos
from bot import Bot
from measuringBot import MeasuringBot
from refPointBot import RefPointBot
from explorerBot import ExplorerBot


pygame.init()
screen = pygame.display.set_mode((1280, 720))

# -------------------
# Global theme of the menus
# -------------------

font = pygame_menu.font.FONT_OPEN_SANS

mytheme = pygame_menu.themes.THEME_DEFAULT.copy()
mytheme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_SIMPLE
mytheme.selection_color = (0,0,0)

<<<<<<< HEAD
 
=======

>>>>>>> ac19b1c29009f16d3831d7969759b7144ebcf916
# -------------------
# "Create your own scenario" menu
# -------------------

scenario_menu = pygame_menu.Menu(400, 600, 'Create your own scenario', mouse_motion_selection=True, theme=mytheme)

scenario_menu.add_button('Return to main menu', pygame_menu.events.BACK)

                     
# -------------------
# Main menu
# -------------------

main_menu = pygame_menu.Menu(400, 600, 'Welcome', mouse_motion_selection=True, theme=mytheme)

def run_demo(name,nb_demo):
    room = Room(1280, 720)
    demos(room,nb_demo)

main_menu.add_selector('Demo :', [('1', 1), ('2', 2),('3',3),('4', 4),('5', 5),('6', 6)], onreturn=run_demo)
main_menu.add_button('Create your own scenario', scenario_menu)
main_menu.add_button('Quit', pygame_menu.events.EXIT)

main_menu.mainloop(screen)