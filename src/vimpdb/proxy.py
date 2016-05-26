import os
import socket
import subprocess

from vimpdb import config
from vimpdb import errors


def get_eggs_paths():
    import vim_bridge
    vimpdb_path = config.get_package_path(errors.ReturnCodeError())
    vim_bridge_path = config.get_package_path(vim_bridge.bridged)
    return (
        os.path.dirname(vimpdb_path),
        os.path.dirname(vim_bridge_path),
        )


class Communicator(object):

    def __init__(self, script, server_name):
        self.script = script
        self.server_name = server_name

    def prepare_subprocess(self, *args):
        parts = self.script.split()
        parts.extend(args)
        return parts

    def _remote_expr(self, expr):
        parts = self.prepare_subprocess('--servername',
                   self.server_name, "--remote-expr", expr)
        p = subprocess.Popen(parts, stdout=subprocess.PIPE)
        return_code = p.wait()
        if return_code:
            raise errors.RemoteUnavailable()
        child_stdout = p.stdout
        output = child_stdout.read()
        return output.strip()

    def _send(self, command):
        # add ':<BS>' to hide last keys sent in VIM command-line
        command = ''.join((command, ':<BS>'))
        parts = self.prepare_subprocess('--servername',
                   self.server_name, "--remote-send", command)
        return_code = subprocess.call(parts)
        if return_code:
            raise errors.RemoteUnavailable()


class ProxyToVim(object):
    """
    use subprocess to launch Vim instance that use clientserver mode
    to communicate with Vim instance used for debugging.
    """

    def __init__(self, communicator):
        self.communicator = communicator

    def _send(self, command):
        self.communicator._send(command)
        config.logger.debug("sent: %s" % command)

    def _remote_expr(self, expr):
        return self.communicator._remote_expr(expr)

    def setupRemote(self):
        if not self.isRemoteSetup():
            # source vimpdb.vim
            proxy_package_path = config.get_package_path(self)
            filename = os.path.join(proxy_package_path, "vimpdb.vim")
            command = "<C-\><C-N>:source %s<CR>" % filename
            self._send(command)
            for egg_path in get_eggs_paths():
                self._send(':call PDB_setup_egg(%s)<CR>' % repr(egg_path))
            self._send(':call PDB_init_controller()')

    def isRemoteSetup(self):
        status = self._expr("exists('*PDB_setup_egg')")
        return status == '1'

    def showFeedback(self, feedback):
        if not feedback:
            return
        feedback_list = feedback.splitlines()
        self.setupRemote()
        self._send(':call PDB_show_feedback(%s)<CR>' % repr(feedback_list))

    def displayLocals(self, feedback):
        if not feedback:
            return
        feedback_list = feedback.splitlines()
        self.setupRemote()
        self._send(':call PDB_reset_watch()<CR>')
        for line in feedback_list:
            self._send(':call PDB_append_watch([%s])<CR>' % repr(line))

    def showFileAtLine(self, filename, lineno):
        if os.path.exists(filename):
            self._showFileAtLine(filename, lineno)

    def _showFileAtLine(self, filename, lineno):
        # Windows compatibility:
        # Windows command-line does not play well with backslash in filename.
        # So turn backslash to slash; Vim knows how to translate them back.
        filename = filename.replace('\\', '/')
        self.setupRemote()
        self._send(':call PDB_show_file_at_line("%s", "%d")<CR>'
            % (filename, lineno))

    def _expr(self, expr):
        config.logger.debug("expr: %s" % expr)
        result = self._remote_expr(expr)
        config.logger.debug("result: %s" % result)
        return result

    # code leftover from hacking
    # def getText(self, prompt):
    #     self.setupRemote()
    #     command = self._expr('PDB_get_command("%s")' % prompt)
    #     return command


class ProxyFromVim(object):

    BUFLEN = 512

    socket_factory = socket.socket

    def __init__(self, port):
        self.socket_inactive = True
        self.port = port

    def bindSocket(self):
        if self.socket_inactive:
            self.socket = self.socket_factory(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', self.port))
            self.socket_inactive = False

    def closeSocket(self):
        if not self.socket_inactive:
            self.socket.close()
            self.socket_inactive = True

    def waitFor(self, pdb):
        self.bindSocket()
        (message, address) = self.socket.recvfrom(self.BUFLEN)
        config.logger.debug("command: %s" % message)
        return message


# code leftover from hacking
# def eat_stdin(self):
#     sys.stdout.write('-- Type Ctrl-D to continue --\n')
#     sys.stdout.flush()
#     sys.stdin.readlines()
