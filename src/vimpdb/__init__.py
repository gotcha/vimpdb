from vimpdb.debugger import set_trace
from vimpdb.debugger import hook


def hookPdb():
    from pdb import Pdb
    hook(Pdb)
