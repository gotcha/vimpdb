import bdb
import pdb
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

    def do_pdb(self, line):
        self.vim.closeSocket()
        self.switchToPdb = True
        return 1

    def postloop(self):
        if self.switchToPdb:
            pdb.set_trace()

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


def set_trace():
    VimPdb().set_trace(sys._getframe().f_back)
