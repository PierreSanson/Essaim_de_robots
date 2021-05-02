import pygame
import pygame_menu

from draw import draw_initial_config
from drawing_to_simulation import load_and_launch_exact_simulation, load_and_launch_discrete_simulation

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

main_menu = pygame_menu.Menu(420, 600, 'Welcome', mouse_motion_selection=True, theme=mytheme)

main_menu.add_button('Initial configuration sketcher', draw_initial_config)
main_menu.add_vertical_margin(20)
main_menu.add_button("Load and launch 'exact' simulation", load_and_launch_exact_simulation)
main_menu.add_button('Load and launch discrete simulation', load_and_launch_discrete_simulation)
main_menu.add_vertical_margin(40)
main_menu.add_button('Quit', pygame_menu.events.EXIT)
main_menu.add_vertical_margin(20)

main_menu.mainloop(screen)
