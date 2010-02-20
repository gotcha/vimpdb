import os
import sys
import pdb
import StringIO
from os.path import exists
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


class Debugger(object):

    def __init__(self):
        self.reset()
        self.setupVim()
        self.commandResult = ''
        self.captured = False

    def setupVim(self):
        # .vim file should initialize a value
        # then instead of initializing each time
        # we can use --remote-expr to evaluate if the vim server is initialized
        filename = os.path.join(getPackagePath(self), "vimpdb.vim")
        command = "<C-\><C-N>:source %s<CR>" % filename
        self.send(command)

    def reset(self):
        self.vim_present = False

    def send(self, command):
        return_code = call([PROGRAM, '--servername', SERVERNAME,
                            '--remote-send', command])
        self.vim_present = return_code == 0

    def expr(self, expr):
        p = Popen([PROGRAM, '--servername',
                   SERVERNAME, "--remote-expr", expr],
            stdin=PIPE, stdout=PIPE)
        return_code = p.wait()
        self.vim_present = return_code == 0
        child_stdout = p.stdout
        return child_stdout.read()

    def gotoline(self, debugger):
        self.setupVim()
        if self.vim_present:
            self.sendgotoline(debugger)

    def sendgotoline(self, debugger):
        frame, lineno = debugger.stack[debugger.curindex]
        filename = debugger.canonic(frame.f_code.co_filename)
        if exists(filename):
            command = ":view %(filename)s<CR>" % dict(filename=filename)
            keys = VIM_KEYS % dict(lineno=lineno)
            self.send("%(command)s%(keys)s" % dict(command=command, keys=keys))

    def reset_stdin(self, debugger):
        sys.stdout.write('-- Type Ctrl-D to continue --\n')
        sys.stdout.flush()
        sys.stdin.readlines()

    def capture_stdout(self):
        self.stdout = sys.stdout
        sys.stdout = StringIO.StringIO()
        self.captured = True

    def reset_stdout(self):
        if self.captured:
            self.captured = False
            self.commandResult = sys.stdout.getvalue()
            sys.stdout = self.stdout

    def preloop(self, debugger):
        if self.vim_present:
            self.gotoline(debugger)

    def precmd(self, debugger):
        self.setupVim()

    def getCommand(self):
        feedback = self.commandResult
        self.commandResult = ''
        self.expr('foreground()')
        return self.expr('VPH_GetCommand("%s")' % feedback)

hook = Debugger()


def precmd(self, line):
    hook.precmd(self)
    return self._orig_precmd(line)


def preloop(self):
    hook.preloop(self)
    return self._orig_preloop()


def default(self, line):
    hook.capture_stdout()
    result = self._orig_default(line)
    hook.reset_stdout()
    return result


def do_vimprompt(self, arg):
    hook.reset_stdout()
    command = hook.getCommand()
    if command == "novimprompt\n":
        hook.reset_stdin(self)
        return
    elif command == "\n":
        command = hook.lastCommand
    elif command == "a\n":
        hook.lastCommand = command
        hook.capture_stdout()
    else:
        hook.lastCommand = command
    self.cmdqueue.append(command)
    self.cmdqueue.append('vimprompt')


def do_vim(self, arg):
    hook.expr('foreground()')
    command = server.run(self)
    if command == "novim":
        hook.reset_stdin(self)
        return
    self.cmdqueue.append(command)
    self.cmdqueue.append('vim')


def setup(klass):

    def setupMethod(klass, method):
        name = method.__name__
        orig = getattr(klass, name)
        setattr(klass, '_orig_' + name, orig)
        setattr(klass, name, method)

    for function in [preloop, default, precmd]:
        setupMethod(klass, function)

    klass.do_vim = do_vim
    klass.do_vimprompt = do_vimprompt


setup(pdb.Pdb)
