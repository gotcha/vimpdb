import os
import os.path
import ConfigParser
from subprocess import call
from subprocess import Popen
from subprocess import PIPE

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


class ReturnCodeError(Exception):
    pass


def getCommandOutput(parts):
    p = Popen(parts, stdin=PIPE, stdout=PIPE)
    return_code = p.wait()
    if return_code:
        raise ReturnCodeError()
    child_stdout = p.stdout
    output = child_stdout.read()
    return output.strip()

NO_SERVER_SUPPORT = "'%s' launches a VIM instance without server support."
NOT_VIM_SCRIPT = "'%s' is not a script that launches a VIM instance."


class Detector(object):

    def __init__(self, config):
        self.script = config.script
        self.server_name = config.server_name
        self.port = config.port
        if not self.check_serversupport():
            raise ValueError(NO_SERVER_SUPPORT % self.script)
        self.check_serverlist()

    def launch(self):
        command = [self.script, '--servername', self.server_name]
        return_code = call(command)
        if return_code:
            raise ReturnCodeError(" ".join(command))

    def get_serverlist(self):
        try:
            return getCommandOutput([self.script, '--serverlist'])
        except ReturnCodeError:
            raise ValueError(NO_SERVER_SUPPORT % self.script)

    def check_serverlist(self):
        serverlist = self.get_serverlist()
        if len(serverlist) == 0:
            self.launch()
        while not serverlist:
            serverlist = self.get_serverlist()
        if self.server_name not in serverlist.lower():
            msg = "'%s' server name not available in server list."
            raise ValueError(msg % self.server_name)

    def check_serversupport(self):
        try:
            version = getCommandOutput([self.script, '--version'])
        except ReturnCodeError:
            raise ValueError(NOT_VIM_SCRIPT % self.script)
        return '+clientserver' in version


if __name__ == '__main__':
    detector = Detector(getConfiguration())
