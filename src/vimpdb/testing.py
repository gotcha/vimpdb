from proxy import ProxyToVim
from StringIO import StringIO

from vimpdb.config import CLIENT
from vimpdb.config import SERVER


class ProxyToVimForTests(ProxyToVim):

    IS_REMOTE_SETUP_IS_FALSE = 0
    IS_REMOTE_SETUP_IS_TRUE = 1

    def __init__(self):
        self.log = StringIO()
        print >> self.log
        self.state = None

    def setState(self, state):
        self.state = state

    def _remote_expr(self, expr):
        result = None
        print >> self.log, "expr: %s" % expr
        if self.state == self.IS_REMOTE_SETUP_IS_TRUE:
            result = '1'
        elif self.state == self.IS_REMOTE_SETUP_IS_FALSE:
            result = '0'
        print >> self.log, "return: %s" % repr(result)
        return result

    def _send(self, command):
        print >> self.log, "send: %s" % command

    def logged(self):
        return self.log.getvalue()


class Config(object):

    def __init__(self, vim_client_script, vim_server_script="server_script",
        server_name='server_name', port=6666):
        self.scripts = dict()
        self.scripts[CLIENT] = vim_client_script
        if vim_server_script is None:
            self.scripts[SERVER] = vim_client_script
        else:
            self.scripts[SERVER] = vim_server_script
        self.server_name = server_name
        self.port = port

config = Config(vim_client_script="bad script")
