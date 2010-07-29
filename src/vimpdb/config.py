import os

PROGRAM = os.environ.get("VIMPDB_VIMSCRIPT", "vim")
SERVERNAME = os.environ.get("VIMPDB_SERVERNAME", "VIMPDB")
PORT = 6666


class Config(object):

    def __init__(self):
        self.script = PROGRAM
        self.server_name = SERVERNAME
        self.port = PORT
