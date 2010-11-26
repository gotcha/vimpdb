import sys
import os
import os.path
import logging
import ConfigParser
from subprocess import call
from subprocess import Popen
from subprocess import PIPE

from vimpdb import bbbconfig
from vimpdb.errors import BadRCFile
from vimpdb.errors import ReturnCodeError
from vimpdb.errors import BrokenConfiguration

RCNAME = os.path.expanduser('~/.vimpdbrc')

CLIENT = 'CLIENT'
SERVER = 'SERVER'


logger = logging.getLogger('vimpdb')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(name)s - %(levelname)s - \
%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Config(object):

    def __init__(self, vim_client_script, vim_server_script, server_name,
        port, loglevel=logging.INFO):
        self.scripts = dict()
        self.scripts[CLIENT] = vim_client_script
        self.scripts[SERVER] = vim_server_script
        self.server_name = server_name
        self.port = port
        self.loglevel = loglevel

    def __repr__(self):
        return ("<vimpdb Config : Script %s; Server name %s, Port %s>" %
          (self.scripts[CLIENT], self.server_name, self.port))

    def __eq__(self, other):
        return (
            self.scripts[CLIENT] == other.scripts[CLIENT] and
            self.scripts[SERVER] == other.scripts[SERVER] and
            self.server_name == other.server_name and
            self.port == other.port)


if sys.platform == 'darwin':
    DEFAULT_CLIENT_SCRIPT = 'mvim'
    DEFAULT_SERVER_SCRIPT = DEFAULT_CLIENT_SCRIPT
elif sys.platform == 'win32':
    DEFAULT_CLIENT_SCRIPT = 'vim.exe'
    DEFAULT_SERVER_SCRIPT = 'gvim.exe'
else:
    DEFAULT_CLIENT_SCRIPT = 'mvim'
    DEFAULT_SERVER_SCRIPT = DEFAULT_CLIENT_SCRIPT

DEFAULT_SERVER_NAME = "VIM"
DEFAULT_PORT = 6666


defaultConfig = Config(DEFAULT_CLIENT_SCRIPT, DEFAULT_SERVER_SCRIPT,
            DEFAULT_SERVER_NAME, DEFAULT_PORT)
defaultConfig.vim_client_script = defaultConfig.scripts[CLIENT]


def getConfiguration(filename=RCNAME):
    if not os.path.exists(filename):
        mustCheck = True
        mustWrite = True
        if bbbconfig.has_environ():
            config = bbbconfig.read_from_environ(Config, defaultConfig)
        else:
            config = defaultConfig
    else:
        mustCheck = False
        mustWrite = False
        try:
            config = read_from_file(filename, Config)
        except BadRCFile, e:
            try:
                config_4_0 = bbbconfig.read_from_file_4_0(filename, Config)
            except BadRCFile:
                raise e
            config = config_4_0
            mustCheck = True
    initial = config
    if mustCheck:
        config = Detector(config).checkConfiguration()
    if mustWrite or initial != config:
        write_to_file(filename, config)
    Detector(config).check_serverlist()
    logger.setLevel(config.loglevel)
    return config


def getRawConfiguration(filename=RCNAME):
    return read_from_file(filename, Config)


def read_from_file(filename, klass):
    parser = ConfigParser.RawConfigParser()
    parser.read(filename)
    if not parser.has_section('vimpdb'):
        raise BadRCFile('[vimpdb] section is missing in "%s"' %
            filename)
    error_msg = ("'%s' option is missing from section [vimpdb] in "
        + "'" + filename + "'.")
    if parser.has_option('vimpdb', 'vim_client_script'):
        vim_client_script = parser.get('vimpdb', 'vim_client_script')
    else:
        raise BadRCFile(error_msg % "vim_client_script")
    if parser.has_option('vimpdb', 'server_name'):
        server_name = parser.get('vimpdb', 'server_name')
    else:
        raise BadRCFile(error_msg % 'server_name')
    if parser.has_option('vimpdb', 'port'):
        port = parser.getint('vimpdb', 'port')
    else:
        raise BadRCFile(error_msg % 'port')
    if parser.has_option('vimpdb', 'vim_server_script'):
        vim_server_script = parser.get('vimpdb', 'vim_server_script')
    else:
        raise BadRCFile(error_msg % "vim_server_script")
    loglevel = logging.INFO
    if parser.has_option('vimpdb', 'loglevel'):
        loglevel = parser.get('vimpdb', 'loglevel')
        if loglevel == 'DEBUG':
            loglevel = logging.DEBUG
    return klass(vim_client_script, vim_server_script, server_name, port,
        loglevel)


def write_to_file(filename, config):
    parser = ConfigParser.RawConfigParser()
    parser.add_section('vimpdb')
    parser.set('vimpdb', 'vim_client_script', config.scripts[CLIENT])
    parser.set('vimpdb', 'vim_server_script', config.scripts[SERVER])
    parser.set('vimpdb', 'server_name', config.server_name)
    parser.set('vimpdb', 'port', config.port)
    rcfile = open(filename, 'w')
    parser.write(rcfile)
    rcfile.close()


def getCommandOutputPosix(parts):
    p = Popen(parts, stdin=PIPE, stdout=PIPE)
    return_code = p.wait()
    if return_code:
        raise ReturnCodeError(return_code, " ".join(parts))
    child_stdout = p.stdout
    output = child_stdout.read()
    return output.strip()


NO_SERVER_SUPPORT = ("'%s' launches a VIM instance without "
    "clientserver support.")
NO_PYTHON_SUPPORT = "'%s' launches a VIM instance without python support."
NO_PYTHON_IN_VERSION = ("Calling --version returned no information "
    "about python support:\n %s")
NO_CLIENTSERVER_IN_VERSION = ("Calling --version returned no information "
    "about clientserver support:\n %s")
RETURN_CODE = "'%s' returned exit code '%d'."


class DetectorBase(object):

    def __init__(self, config, commandParser):
        self.scripts = dict()
        self.scripts[CLIENT] = config.scripts[CLIENT]
        self.scripts[SERVER] = config.scripts[SERVER]
        self.server_name = config.server_name
        self.port = config.port
        self.commandParser = commandParser

    def checkConfiguration(self):
        while not self._checkConfiguration():
            pass
        return self

    def _checkConfiguration(self):
        try:
            self.check_clientserver_support(CLIENT)
        except ValueError, e:
            print e.args[0]
            self.query_script(CLIENT)
            return False
        try:
            self.check_python_support()
        #XXX catch WindowsError
        except OSError, e:
            print e.args[1]
            server_script = self.scripts[SERVER]
            if server_script == DEFAULT_SERVER_SCRIPT:
                print ("with the default VIM server script (%s)."
                    % server_script)
            else:
                print ("with the VIM server script from the configuration "
                    "(%s)." % server_script)
            self.query_script(SERVER)
            return False
        except ValueError, e:
            print e.args[0]
            self.query_script(SERVER)
            return False
        try:
            self.check_server_clientserver_support()
        except ValueError, e:
            print e.args[0]
            self.query_script(SERVER)
            return False
        try:
            self.check_serverlist()
        except ValueError, e:
            print e.args[0]
            self.query_servername()
            return False
        return True

    def launch_vim_server(self):
        raise NotImplemented

    def build_command(self, script_type, *args):
        script = self.scripts[script_type]
        command = script.split()
        command.extend(args)
        return command

    def get_serverlist(self):
        command = self.build_command(CLIENT, '--serverlist')
        try:
            return self.commandParser(command)
        except ReturnCodeError, e:
            return_code = e.args[0]
            command = e.args[1]
            raise ValueError(RETURN_CODE % (command, return_code))

    def check_serverlist(self):
        serverlist = self.get_serverlist()
        if len(serverlist) == 0:
            try:
                self.launch_vim_server()
            except ReturnCodeError, e:
                return_code = e.args[0]
                command = e.args[1]
                raise ValueError(RETURN_CODE % (command, return_code))
        # XXX add a timeout to the loop
        while not serverlist:
            serverlist = self.get_serverlist()
        if self.server_name.lower() not in serverlist.lower():
            msg = "'%s' server name not available in server list:\n%s"
            raise ValueError(msg % (self.server_name, serverlist))
        return True

    def get_vim_version(self, script_type):
        try:
            command = self.build_command(script_type, '--version')
            return self.commandParser(command)
        except ReturnCodeError, e:
            return_code = e.args[0]
            command = e.args[1]
            raise ValueError(RETURN_CODE % (command, return_code))

    def check_clientserver_support(self, script_type):
        version = self.get_vim_version(script_type)
        if '+clientserver' in version:
            return True
        elif '-clientserver' in version:
            raise ValueError(NO_SERVER_SUPPORT % self.scripts[script_type])
        else:
            raise ValueError(NO_CLIENTSERVER_IN_VERSION % version)

    def check_server_clientserver_support(self):
        raise NotImplemented

    def check_python_support(self):
        raise NotImplemented

    def query_script(self, script_type):
        if script_type == CLIENT:
            type = 'client'
        else:
            type = 'server'
        question = ("Input another VIM %s script (leave empty to abort): "
            % type)
        answer = raw_input(question)
        if answer == '':
            raise BrokenConfiguration
        else:
            self.scripts[script_type] = answer

    def query_servername(self):
        question = "Input another server name (leave empty to abort): "
        answer = raw_input(question)
        if answer == '':
            raise BrokenConfiguration
        else:
            self.server_name = answer

if sys.platform == 'win32':

    def getCommandOutputWindows(parts):
        try:
            return getCommandOutputPosix(parts)
        except WindowsError:
            raise ReturnCodeError(1, " ".join(parts))

    class Detector(DetectorBase):

        def __init__(self, config, commandParser=getCommandOutputWindows):
            return super(Detector, self).__init__(config, commandParser)

        def check_python_support(self):
            command = self.build_command(SERVER, 'dummy.txt',
                '+exe \'if has("python") | :q | else | :cq | endif\'')
            return_code = call(command)
            if return_code:
                raise ValueError(NO_PYTHON_SUPPORT % self.scripts[SERVER])
            else:
                return True

        def check_server_clientserver_support(self):
            command = self.build_command(SERVER, 'dummy.txt',
                '+exe \'if has("clientserver") | :q | else | :cq | endif\'')
            return_code = call(command)
            if return_code:
                raise ValueError(NO_SERVER_SUPPORT % self.scripts[SERVER])
            else:
                return True

        def launch_vim_servers(self):
            command = self.build_command(SERVER, '--servername',
                self.server_name)
            Popen(command, stdin=PIPE, stdout=PIPE)
            return True

else:

    class Detector(DetectorBase):

        def __init__(self, config, commandParser=getCommandOutputPosix):
            return super(Detector, self).__init__(config, commandParser)

        def check_python_support(self):
            version = self.get_vim_version(SERVER)
            if '+python' in version:
                return True
            elif '-python' in version:
                raise ValueError(NO_PYTHON_SUPPORT % self.scripts[SERVER])
            else:
                raise ValueError(NO_PYTHON_IN_VERSION % version)

        def check_server_clientserver_support(self):
            return self.check_clientserver_support(SERVER)

        def launch_vim_server(self):
            command = self.build_command(SERVER, '--servername',
                self.server_name)
            return_code = call(command)
            if return_code:
                raise ReturnCodeError(return_code, " ".join(command))
            return True
