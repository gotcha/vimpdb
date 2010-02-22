import os
import sys
import pdb
import StringIO
from subprocess import call
from subprocess import Popen
from subprocess import PIPE
from vimpdb import server

VIM_KEYS = "%(lineno)dgg:setlocal cursorline<CR>zz"

PROGRAM = os.environ.get("VIMPDB_VIMSCRIPT", "vimpdb")
SERVERNAME = os.environ.get("VIMPDB_SERVERNAME", "VIMPDB")


def getPackagePath(instance):
    module = sys.modules[instance.__module__]
    return os.path.dirname(module.__file__)


class ProxyToVim(object):

    def __init__(self):
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
        return self._expr('PDB_GetCommand("%s")' % prompt)

    def showFeedback(self, feedback):
        self._expr('PDB_Feedback("%s")' % feedback)

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


class Debugger(object):

    def __init__(self):
        self.vim = ProxyToVim()
        self.textOutput = ''
        self.captured = False
        self.vimhttp = False
        self.vimprompt = False

    def getFileAndLine(self, debugger):
        frame, lineno = debugger.stack[debugger.curindex]
        filename = debugger.canonic(frame.f_code.co_filename)
        return filename, lineno

    def reset_stdin(self, debugger):
        sys.stdout.write('-- Type Ctrl-D to continue --\n')
        sys.stdout.flush()
        sys.stdin.readlines()

    def capture_stdout(self):
        #print "capture"
        self.stdout = sys.stdout
        sys.stdout = StringIO.StringIO()
        self.captured = True

    def reset_stdout(self):
        if self.captured:
            self.captured = False
            self.textOutput = sys.stdout.getvalue()
            sys.stdout = self.stdout
        #print "reset"

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


hook = Debugger()


def precmd(self, line):
    hook.vim.setupRemote()
    return self._orig_precmd(line)


def preloop(self):
    filename, lineno = hook.getFileAndLine(self)
    hook.vim.showFileAtLine(filename, lineno)
    return self._orig_preloop()


def default(self, line):
    hook.capture_stdout()
    result = self._orig_default(line)
    hook.reset_stdout()
    return result


def do_vimprompt(self, arg):
    hook.enterVimPromptMode()
    hook.reset_stdout()
    hook.vim.foreground()
    prompt = hook.pop_output()
    command = hook.vim.getText(prompt)
    if command == "novimprompt\n":
        hook.reset_stdin(self)
        hook.exitVimPromptMode()
        return
    elif command == "\n":
        command = hook.lastCommand
    elif command.strip() in ["a", "args", "u", "up", "d", "down"]:
        hook.lastCommand = command
        hook.capture_stdout()
    else:
        hook.lastCommand = command
    self.cmdqueue.append(command)
    self.cmdqueue.append('vimprompt')


def do_vim(self, arg):
    hook.enterVimMode()
    hook.vim.foreground()
    command = server.run(self)
    if command == "novim":
        hook.reset_stdin(self)
        hook.exitVimMode()
        return
    elif command.strip() in ["a", "args", "u", "up", "d", "down"]:
        hook.capture_stdout()
    self.cmdqueue.append(command)
    self.cmdqueue.append('vim')


def postcmd(self, stop, line):
    cmd = line.strip()
    if cmd in ["a", "args", "u", "up", "d", "down"]:
        hook.reset_stdout()
        filename, lineno = hook.getFileAndLine(self)
        hook.vim.showFileAtLine(filename, lineno)
    hook.vim.showFeedback(self.pop_output())
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
    klass.do_vimprompt = do_vimprompt


setup(pdb.Pdb)
