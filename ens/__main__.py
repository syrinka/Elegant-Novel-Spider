import sys

from ens.cli import ens_cli
from ens.console import console


def run():
    try:
        ens_cli()
    except Exception as e:
        console.print_exception()
        sys.exit(1)


if __name__ == '__main__':
    run()
