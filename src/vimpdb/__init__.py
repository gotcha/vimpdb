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
        self.vim = False
        self.vimprompt = False

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
        #print "send", command
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

    def getFileAndLine(self, debugger):
        frame, lineno = debugger.stack[debugger.curindex]
        filename = debugger.canonic(frame.f_code.co_filename)
        return filename, lineno

    def sendgotoline(self, debugger):
        filename, lineno = self.getFileAndLine(debugger)
        if exists(filename):
            command = ":view %(filename)s<CR>" % dict(filename=filename)
            keys = VIM_KEYS % dict(lineno=lineno)
            self.send("%(command)s%(keys)s" % dict(command=command, keys=keys))

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
            self.commandResult = sys.stdout.getvalue()
            sys.stdout = self.stdout
        #print "reset"

    def preloop(self, debugger):
        if self.vim_present:
            self.gotoline(debugger)

    def precmd(self, debugger):
        self.setupVim()

    def getCommand(self):
        feedback = self.commandResult
        self.commandResult = ''
        self.expr('foreground()')
        return self.expr('PDB_GetCommand("%s")' % feedback)

    def enterVimMode(self):
        if not self.vim:
            print "Entering Vim mode"
            self.vim = True
        self.expr('foreground()')

    def exitVimMode(self):
        self.vim = False

    def enterVimPromptMode(self):
        if not self.vimprompt:
            print "Entering Vim mode"
            self.vimprompt = True

    def exitVimPromptMode(self):
        self.vimprompt = False

    def sendFeedback(self):
        self.expr('PDB_Feedback("%s")' % self.commandResult)
        self.commandResult = ''

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
    hook.enterVimPromptMode()
    hook.reset_stdout()
    command = hook.getCommand()
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
        hook.sendgotoline(self)
    hook.sendFeedback()
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
