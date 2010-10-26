import sys
import os
import os.path
import ConfigParser
from subprocess import call
from subprocess import Popen
from subprocess import PIPE

RCNAME = os.path.expanduser('~/.vimpdbrc')

if sys.platform == 'darwin':
    PLATFORM_SCRIPT = 'mvim'
elif sys.platform == 'windows':
    PLATFORM_SCRIPT = 'vim.exe'
else:
    PLATFORM_SCRIPT = 'mvim'

DEFAULT_SCRIPT = os.environ.get("VIMPDB_VIMSCRIPT", PLATFORM_SCRIPT)
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
            self.write_to_file(
                DEFAULT_SCRIPT, DEFAULT_SERVERNAME, DEFAULT_PORT)
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

    def write_to_file(self, script, server_name, port):
        parser = ConfigParser.RawConfigParser()
        parser.add_section('vimpdb')
        parser.set('vimpdb', 'script', script)
        parser.set('vimpdb', 'server_name', server_name)
        parser.set('vimpdb', 'port', port)
        rcfile = open(self.filename, 'w')
        parser.write(rcfile)
        rcfile.close()

    def __repr__(self):
        return ("<vimpdb Config : Script %s; Server name %s, Port %s>" %
          (self.script, self.server_name, self.port))


def getConfiguration():
    return Config(RCNAME)


class ReturnCodeError(Exception):
    pass


class NoWorkingConfigurationError(Exception):
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

    def __init__(self, config, commandParser=getCommandOutput):
        self.script = config.script
        self.server_name = config.server_name
        self.port = config.port
        self.commandParser = commandParser

    def checkConfiguration(self):
        while not self._checkConfiguration():
            pass
        self.config = self.store_config()
        return self

    def _checkConfiguration(self):
        try:
            self.check_python_support()
        except OSError, e:
            print e.args[1]
            if self.script == DEFAULT_SCRIPT:
                print "with the default script (%s)." % self.script
            else:
                print ("with the script from the configuration (%s)."
                    % self.script)
            self.query_script()
            return False
        except ValueError, e:
            print e.args[0]
            self.query_script()
            return False
        try:
            self.check_server_support()
        except ValueError, e:
            print e.args[0]
            self.query_script()
            return False
        try:
            self.check_serverlist()
        except ValueError, e:
            print e.args[0]
            self.query_servername()
            return False
        return True

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
            return self.commandParser(command)
        except ReturnCodeError:
            raise ValueError(NO_SERVER_SUPPORT % self.script)

    def check_serverlist(self):
        serverlist = self.get_serverlist()
        if len(serverlist) == 0:
            self.launch()
        while not serverlist:
            serverlist = self.get_serverlist()
        if self.server_name.lower() not in serverlist.lower():
            msg = "'%s' server name not available in server list.\n%s"
            raise ValueError(msg % (self.server_name, serverlist))

    def get_vim_version(self):
        try:
            command = self.build_command('--version')
            version = self.commandParser(command)
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

    def query_script(self):
        question = "Input another script (leave empty to abort): "
        answer = raw_input(question)
        if answer == '':
            raise NoWorkingConfigurationError
        else:
            self.script = answer

    def query_servername(self):
        question = "Input another server name (leave empty to abort): "
        answer = raw_input(question)
        if answer == '':
            raise NoWorkingConfigurationError
        else:
            self.server_name = answer

    def store_config(self):
        config = getConfiguration()
        config.write_to_file(self.script, self.server_name, self.port)
        return config


if __name__ == '__main__':
    detector = Detector(getConfiguration())
    detector.checkConfiguration()
    print detector.config
