import bdb
from pdb import Pdb
import sys
import StringIO
from vimpdb.proxy import ProxyToVim


class VimPdb(Pdb):

    def __init__(self):
        bdb.Bdb.__init__(self)
        self.aliases = {}
        self.vim = ProxyToVim()
        self.mainpyfile = ''
        self._wait_for_mainpyfile = 0
        self.switchToPdb = False

    def xxx_interaction(self, frame, traceback):
        self.setup(frame, traceback)
        self.cmdloop()
        self.forget()

    def trace_dispatch(self, frame, event, arg):
        if self.switchToPdb:
            return
        return Pdb.trace_dispatch(self, frame, event, arg)

    def execRcLines(self):
        pass

    def cmdloop(self):
        stop = None
        self.preloop()
        while not stop:
            line = self.vim.waitFor(self)
            line = self.precmd(line)
            stop = self.onecmd(line)
            stop = self.postcmd(stop, line)
        self.postloop()

    def postloop(self):
        if self.switchToPdb:
            hooked_set_trace()

    def getFileAndLine(self):
        frame, lineno = self.stack[self.curindex]
        filename = self.canonic(frame.f_code.co_filename)
        return filename, lineno

    def preloop(self):
        filename, lineno = self.getFileAndLine()
        self.vim.showFileAtLine(filename, lineno)

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

    def onecmd(self, line):
        self.capture_stdout()
        stop = Pdb.onecmd(self, line)
        self.stop_capture()
        self.vim.showFeedback(self.pop_output())
        return stop

    def postcmd(self, stop, line):
        cmd = line.strip()
        if cmd in ["a", "args", "u", "up", "d", "down"]:
            filename, lineno = self.getFileAndLine()
            self.vim.showFileAtLine(filename, lineno)
        stop = Pdb.postcmd(self, stop, line)
        return stop

    def do_pdb(self, line):
        self.vim.closeSocket()
        self.switchToPdb = True
        sys.set_trace = None
        return 1


def set_trace():
    VimPdb().set_trace(sys._getframe().f_back)

# hook vimpdb  #
################


def trace_dispatch(self, frame, event, arg):
    if hasattr(self, 'switchToVim'):
        return
    return self._orig_trace_dispatch(frame, event, arg)


def do_vim(self, arg):
    self.switchToVim = True
    return 1


def postloop(self):
    if hasattr(self, 'switchToVim'):
        set_trace()


def hook(klass):

    def setupMethod(klass, method):
        name = method.__name__
        orig = getattr(klass, name)
        orig_attr = '_orig_' + name
        if not hasattr(klass, orig_attr):
            setattr(klass, '_orig_' + name, orig)
            setattr(klass, name, method)

    setupMethod(klass, trace_dispatch)
    if not hasattr(klass, 'do_vim'):
        klass.do_vim = do_vim
        klass.postloop = postloop


def hooked_set_trace():
    hook(Pdb)
    pdb_debugger = Pdb()
    pdb_debugger.set_trace(sys._getframe().f_back)
