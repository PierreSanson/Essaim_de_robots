# Interface en ligne de commande pour le lancement de la simulation
import click

from drawing_to_simulation import load_and_launch_simulation

@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('-m','--multiple', default=1, help='Runs the simulation X times.')       

def sim(filename,multiple):
    if multiple == 1:
        load_and_launch_simulation(filename)
    else:
        with click.progressbar(list(range(multiple))) as bar:
            for attempt in bar:
                load_and_launch_simulation(filename)


if __name__ == '__main__':
    sim()