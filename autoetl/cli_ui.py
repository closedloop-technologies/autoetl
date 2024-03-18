import pyfiglet
from autoetl import name as NAME


def banner():
    return pyfiglet.figlet_format(NAME, font="slant").rstrip()
