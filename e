#/bin/env python3
from ens.config import DEBUG
from ens.console import console
from ens.exceptions import ENSError
from ens.cli import ens_cli
    
try:
    ens_cli()
except ENSError as e:
    if DEBUG:
        console.print_exception()
    else:
        console.print(e)
except Exception as e:
    console.print_exception()