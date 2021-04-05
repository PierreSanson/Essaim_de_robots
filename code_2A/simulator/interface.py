import pygame, pygame_menu

from main import Room, demos
from bot import Bot
from measuringBot import MeasuringBot
from refPointBot import RefPointBot
from explorerBot import ExplorerBot

from draw import draw_initial_config
from drawing_to_simulation import load_and_launch_simulation

pygame.init()

sw, sh = 1600, 900  # screenWidth, screenHeight
screen = pygame.display.set_mode((sw, sh))

# -------------------
# Global theme of the menus
# -------------------

font = pygame_menu.font.FONT_OPEN_SANS

mytheme = pygame_menu.themes.THEME_DEFAULT.copy()
mytheme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_SIMPLE
mytheme.selection_color = (0,0,0)

                     
# -------------------
# Main menu
# -------------------

main_menu = pygame_menu.Menu(400, 600, 'Welcome', mouse_motion_selection=True, theme=mytheme)

main_menu.add_button('Initial configuration sketcher', draw_initial_config)
main_menu.add_button('Load and launch simulation', load_and_launch_simulation)
main_menu.add_vertical_margin(100)
main_menu.add_button('Quit', pygame_menu.events.EXIT)

main_menu.mainloop(screen)