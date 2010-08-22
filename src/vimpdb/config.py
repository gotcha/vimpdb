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
NO_PYTHON_SUPPORT = "'%s' launches a VIM instance without python support."
NOT_VIM_SCRIPT = "'%s' is not a script that launches a VIM instance."
WRONG_SCRIPT = "'%s' is a script that does not support --version option."


class Detector(object):

    def __init__(self, config):
        self.script = config.script
        self.server_name = config.server_name
        self.port = config.port

    def checkConfiguration(self):
        self.check_python_support()
        self.check_server_support()
        self.check_serverlist()
        return self

    def launch(self):
        command = self.build_command('--servername', self.server_name)
        return_code = call(command)
        if return_code:
            raise ReturnCodeError(" ".join(command))

    def build_command(self, *args):
        command = self.script.split()
        command.extend(args)
        return command

    def get_serverlist(self):
        try:
            command = self.build_command('--serverlist')
            return getCommandOutput(command)
        except ReturnCodeError:
            raise ValueError(NO_SERVER_SUPPORT % self.script)

    def check_serverlist(self):
        serverlist = self.get_serverlist()
        if len(serverlist) == 0:
            self.launch()
        while not serverlist:
            serverlist = self.get_serverlist()
        if self.server_name.lower() not in serverlist.lower():
            msg = "'%s' server name not available in server list."
            raise ValueError(msg % self.server_name)

    def get_vim_version(self):
        try:
            command = self.build_command('--version')
            version = getCommandOutput(command)
        except ReturnCodeError:
            raise ValueError(WRONG_SCRIPT % self.script)
        return version

    def check_server_support(self):
        version = self.get_vim_version()
        if '+clientserver' in version:
            return
        elif '-clientserver' in version:
            raise ValueError(NO_SERVER_SUPPORT % self.script)
        else:
            raise ValueError(NOT_VIM_SCRIPT % self.script)

    def check_python_support(self):
        version = self.get_vim_version()
        if '+python' in version:
            return
        elif '-python' in version:
            raise ValueError(NO_PYTHON_SUPPORT % self.script)
        else:
            raise ValueError(NOT_VIM_SCRIPT % self.script)


if __name__ == '__main__':
    detector = Detector(getConfiguration())
