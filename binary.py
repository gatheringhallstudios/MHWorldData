import click
import sys

from mhdata.merge import mhwdb, binary

# todo: organize

if sys.version_info < (3,6):
    print("This application has designed for python 3.6 and later")
    exit(1)

@click.group(name="binary")
def binary_cmd():
    "Commands to work with binary data."

@binary_cmd.command()
def update():
    "Performs an update using ingame binaries"
    binary.update_all()

@binary_cmd.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('outfile', type=click.File('w', 'utf8'))
def dump(file, outfile: click.File):
    "Parses and dumps the file into stdout"
    dumped = binary.dump_file(click.format_filename(file))
    outfile.write(dumped)

if __name__ == '__main__':
    binary_cmd()