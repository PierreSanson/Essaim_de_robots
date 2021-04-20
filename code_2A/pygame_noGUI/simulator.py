# Interface en ligne de commande pour le lancement de la simulation

import click

from draw import draw_initial_config
from drawing_to_simulation import load_and_launch_simulation

@click.command()
@click.option('-d','--draw', is_flag=True, help='Opens up simple editor to draw a starting configuration.')
@click.option('-r','--run', default='nothing', help='Runs the simulation from the given starting configuration.')       

def sim(draw,run):
    if draw:
        draw_initial_config()
    
    if run != 'nothing':
        load_and_launch_simulation(run)



if __name__ == '__main__':
    sim()