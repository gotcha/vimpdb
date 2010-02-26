import os
import sys
#import pdb
import StringIO
import socket
from subprocess import call
from subprocess import Popen
from subprocess import PIPE

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
        self.foreground()

    def setupRemote(self):
        if not self.isRemoteSetup():
            filename = os.path.join(getPackagePath(self), "vimpdb.vim")
            command = "<C-\><C-N>:source %s<CR>" % filename
            self._send(command)

    def foreground(self):
        self._send(':call foreground()<CR>')

    def getText(self, prompt):
        command = self._expr('PDB_GetCommand("%s")' % prompt)
        return command

    def waitFor(self, pdb):
        (message, address) = self.server.recvfrom(self.BUFLEN)
        print "command :", message
        return message

    def showFeedback(self, feedback):
        if not feedback:
            return
        feedback_list = feedback.splitlines()
        self._send(':call PDB_Feedback(%s)<CR>' % repr(feedback_list))

    def showFileAtLine(self, filename, lineno):
        if os.path.exists(filename):
            self._showFileAtLine(filename, lineno)

    def _send(self, command):
        return_code = call([PROGRAM, '--servername', SERVERNAME,
                            '--remote-send', command])
        if return_code:
            raise RemoteUnavailable()
        print "sent :", command

    def _showFileAtLine(self, filename, lineno):
        self._send(':call PDB_ShowFileAtLine("%s", "%d")<CR>'
            % (filename, lineno))

    def _expr(self, expr):
        print "expr :", expr
        self._checkRemote()
        result = self._remote_expr(expr)
        print result
        return result

    def _remote_expr(self, expr):
        p = Popen([PROGRAM, '--servername',
                   SERVERNAME, "--remote-expr", expr],
            stdin=PIPE, stdout=PIPE)
        return_code = p.wait()
        if return_code:
            raise RemoteUnavailable()
        child_stdout = p.stdout
        output = child_stdout.read()
        return output.strip()

    def isRemoteSetup(self):
        status = self._remote_expr("exists('*PDB_Init')")
        return status == '1'

    def _checkRemote(self):
        self.setupRemote()


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


vim = None #ProxyToVim()
io = None #PDBIO()


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


#setup(pdb.Pdb)
