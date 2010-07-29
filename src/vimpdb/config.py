import os
import os.path
import ConfigParser

RCNAME = os.path.expanduser('~/.vimpdbrc')

DEFAULT_SCRIPT = os.environ.get("VIMPDB_VIMSCRIPT", "vim")
DEFAULT_SERVERNAME = os.environ.get("VIMPDB_SERVERNAME", "VIMPDB")
DEFAULT_PORT = 6666


class BadConfiguration(Exception):
    pass


class Config(object):

    def __init__(self, filename):
        self.filename = filename
        self.read_from_file()

    def read_from_file(self):
        if not os.path.exists(self.filename):
            self.write_to_file()
        parser = ConfigParser.RawConfigParser()
        parser.read(self.filename)
        if not parser.has_section('vimpdb'):
            raise BadConfiguration('[vimpdb] section is missing in "%s"' %
                self.filename)
        error_msg = ("'%s' option is missing from section [vimpdb] in "
            + "'" + self.filename + "'.")
        if parser.has_option('vimpdb', 'script'):
            self.script = parser.get('vimpdb', 'script')
        else:
            raise BadConfiguration(error_msg % 'script')
        if parser.has_option('vimpdb', 'server_name'):
            self.server_name = parser.get('vimpdb', 'server_name')
        else:
            raise BadConfiguration(error_msg % 'server_name')
        if parser.has_option('vimpdb', 'port'):
            self.port = parser.getint('vimpdb', 'port')
        else:
            raise BadConfiguration(error_msg % 'port')

    def write_to_file(self):
        parser = ConfigParser.RawConfigParser()
        parser.add_section('vimpdb')
        parser.set('vimpdb', 'script', DEFAULT_SCRIPT)
        parser.set('vimpdb', 'server_name', DEFAULT_SERVERNAME)
        parser.set('vimpdb', 'port', DEFAULT_PORT)
        rcfile = open(self.filename, 'w')
        parser.write(rcfile)
        rcfile.close()


def getConfiguration():
    return Config(RCNAME)
