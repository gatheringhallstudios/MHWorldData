import click

from build import build_database

@click.command()
def build():
    output_filename = 'mhw.db'
    build_database(output_filename)
    
if __name__ == '__main__':
    build()