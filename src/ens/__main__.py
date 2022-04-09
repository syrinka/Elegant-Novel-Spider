from ens.console import console
from ens.exceptions import ENSError, Abort

if __name__ == '__main__':

    from ens.cli import ens_cli
    
    try:
        ens_cli()
    except Abort:
        console.print('Aborted!')
    except ENSError as e:
        console.print(e)
    except Exception as e:
        console.print_exception()
