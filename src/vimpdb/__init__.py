import os
import sys
import pdb
import StringIO
import socket
from subprocess import call
from subprocess import Popen
from subprocess import PIPE

VIM_KEYS = "%(lineno)dgg:setlocal cursorline<CR>zz"

PROGRAM = os.environ.get("VIMPDB_VIMSCRIPT", "vimpdb")
SERVERNAME = os.environ.get("VIMPDB_SERVERNAME", "VIMPDB")


def getPackagePath(instance):
    module = sys.modules[instance.__module__]
    return os.path.dirname(module.__file__)


class ProxyToVim(object):

    PORT = 6666
    BUFLEN = 512

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
            socket.IPPROTO_UDP)
        self.server.bind(('', self.PORT))
        self.setupRemote()

    def setupRemote(self):
        self.remoteVimAvailable = False
        # .vim file should initialize a value
        # then instead of initializing each time
        # we can use --remote-expr to evaluate if the vim server is initialized
        filename = os.path.join(getPackagePath(self), "vimpdb.vim")
        command = "<C-\><C-N>:source %s<CR>" % filename
        self._send(command)

    def foreground(self):
        self._expr('foreground()')

    def getText(self, prompt):
        command = self._expr('PDB_GetCommand("%s")' % prompt)
        return command.strip()

    def waitFor(self, pdb):
        (message, address) = self.server.recvfrom(self.BUFLEN)
        #info("RCV: from %s: %s" % ( address, message))
        return message.strip()

    def showFeedback(self, feedback):
        feedback_list = feedback.splitlines()
        self._expr('PDB_Feedback(%s)' % repr(feedback_list))

    def showFileAtLine(self, filename, lineno):
        if os.path.exists(filename):
            self._showFileAtLine(filename, lineno)

    def _send(self, command):
        return_code = call([PROGRAM, '--servername', SERVERNAME,
                            '--remote-send', command])
        self.remoteVimAvailable = return_code == 0

    def _showFileAtLine(self, filename, lineno):
        command = ":view %(filename)s<CR>" % dict(filename=filename)
        keys = VIM_KEYS % dict(lineno=lineno)
        self._checkRemote()
        self._send("%(command)s%(keys)s" % dict(command=command, keys=keys))

    def _expr(self, expr):
        self._checkRemote()
        p = Popen([PROGRAM, '--servername',
                   SERVERNAME, "--remote-expr", expr],
            stdin=PIPE, stdout=PIPE)
        return_code = p.wait()
        self.remoteVimAvailable = return_code == 0
        child_stdout = p.stdout
        return child_stdout.read()

    def _checkRemote(self):
        self.setupRemote()
        if not self.remoteVimAvailable:
            raise RemoteUnavailable()


class RemoteUnavailable(Exception):
    pass


class PDBIO(object):

    def __init__(self):
        self.textOutput = ''
        self.captured = False
        self.vimhttp = False
        self.vimprompt = False

    def eat_stdin(self):
        sys.stdout.write('-- Type Ctrl-D to continue --\n')
        sys.stdout.flush()
        sys.stdin.readlines()

    def capture_stdout(self):
        self.stdout = sys.stdout
        sys.stdout = StringIO.StringIO()
        self.captured = True

    def stop_capture(self):
        if self.captured:
            self.captured = False
            self.textOutput = sys.stdout.getvalue()
            sys.stdout = self.stdout

    def pop_output(self):
        result = self.textOutput
        self.textOutput = ''
        return result

    def enterVimMode(self):
        if not self.vimhttp:
            print "Entering Vim mode"
            self.vimhttp = True

    def exitVimMode(self):
        self.vimhttp = False

    def enterVimPromptMode(self):
        if not self.vimprompt:
            print "Entering Vim mode"
            self.vimprompt = True

    def exitVimPromptMode(self):
        self.vimprompt = False


vim = ProxyToVim()
io = PDBIO()


def getFileAndLine(self):
    frame, lineno = self.stack[self.curindex]
    filename = self.canonic(frame.f_code.co_filename)
    return filename, lineno


def precmd(self, line):
    vim.setupRemote()
    return self._orig_precmd(line)


def preloop(self):
    filename, lineno = self.getFileAndLine()
    vim.showFileAtLine(filename, lineno)
    return self._orig_preloop()


def default(self, line):
    io.capture_stdout()
    result = self._orig_default(line)
    io.stop_capture()
    return result


def do_vimp(self, arg):
    io.enterVimPromptMode()
    io.stop_capture()
    vim.foreground()
    prompt = io.pop_output()
    command = vim.getText(prompt)
    if command == "pdb":
        io.eat_stdin()
        io.exitVimPromptMode()
        return
    elif command == "":
        command = io.lastCommand
    elif command in ["a", "args", "u", "up", "d", "down"]:
        io.lastCommand = command
        io.capture_stdout()
    else:
        io.lastCommand = command
    self.cmdqueue.append(command)
    self.cmdqueue.append('vimp')


def do_vim(self, arg):
    io.enterVimMode()
    vim.foreground()
    command = vim.waitFor(self)
    if command == "pdb":
        io.eat_stdin()
        io.exitVimMode()
        return
    elif command in ["a", "args", "u", "up", "d", "down"]:
        io.capture_stdout()
    self.cmdqueue.append(command)
    self.cmdqueue.append('vim')


def postcmd(self, stop, line):
    cmd = line.strip()
    if cmd in ["a", "args", "u", "up", "d", "down"]:
        io.stop_capture()
        filename, lineno = self.getFileAndLine()
        vim.showFileAtLine(filename, lineno)
    vim.showFeedback(io.pop_output())
    return self._orig_postcmd(stop, line)


def setup(klass):

    def setupMethod(klass, method):
        name = method.__name__
        orig = getattr(klass, name)
        setattr(klass, '_orig_' + name, orig)
        setattr(klass, name, method)

    for function in [preloop, default, precmd, postcmd]:
        setupMethod(klass, function)

    klass.do_vim = do_vim
    klass.do_vimp = do_vimp
    klass.getFileAndLine = getFileAndLine


setup(pdb.Pdb)
