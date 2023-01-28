from ens.console import console
from ens.exceptions import ENSError
from ens.cli import ens_cli


def run():
    try:
        ens_cli()
    except Exception as e:
        console.print_exception()
        exit(1)


if __name__ == '__main__':
    run()
