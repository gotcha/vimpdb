import os
import sys
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
        self.socket_inactive = True
        self.bindSocket()
        self.setupRemote()
        self.foreground()
        self.comm_init()

    def comm_init(self):
        self._send(':call PDB_comm_init()<CR>')

    def bindSocket(self):
        if self.socket_inactive:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                socket.IPPROTO_UDP)
            self.socket.bind(('', self.PORT))
            self.socket_inactive = False

    def closeSocket(self):
        self.socket.close()
        self.socket_inactive = True

    def setupRemote(self):
        if not self.isRemoteSetup():
            filename = os.path.join(getPackagePath(self), "vimpdb.vim")
            command = "<C-\><C-N>:source %s<CR>" % filename
            self._send(command)

    def foreground(self):
        self._send(':call foreground()<CR>')

    def getText(self, prompt):
        self.setupRemote()
        command = self._expr('PDB_get_command("%s")' % prompt)
        return command

    def waitFor(self, pdb):
        self.bindSocket()
        (message, address) = self.socket.recvfrom(self.BUFLEN)
        print "command:", message
        return message

    def showFeedback(self, feedback):
        if not feedback:
            return
        feedback_list = feedback.splitlines()
        self.setupRemote()
        self._send(':call PDB_display_feedback(%s)<CR>' % repr(feedback_list))

    def showFileAtLine(self, filename, lineno):
        if os.path.exists(filename):
            self._showFileAtLine(filename, lineno)

    def _send(self, command):
        return_code = call([PROGRAM, '--servername', SERVERNAME,
                            '--remote-send', command])
        if return_code:
            raise RemoteUnavailable()
        print "sent:", command

    def _showFileAtLine(self, filename, lineno):
        self.setupRemote()
        # Windows compatibility:
        # Command-line does not play well with backslash in filename.
        # So turn backslash to slash; Vim knows how to translate them back.
        filename = filename.replace('\\', '/')
        self._send(':call PDB_show_file_at_line("%s", "%d")<CR>'
            % (filename, lineno))

    def _expr(self, expr):
        print "expr:", expr
        result = self._remote_expr(expr)
        print "result:", result
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
        status = self._remote_expr("exists('*PDB_init')")
        return status == '1'


class RemoteUnavailable(Exception):
    pass


def eat_stdin(self):
    sys.stdout.write('-- Type Ctrl-D to continue --\n')
    sys.stdout.flush()
    sys.stdin.readlines()
