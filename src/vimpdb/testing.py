from vimpdb.proxy import ProxyToVim
from vimpdb.debugger import StringIO


class ProxyToVimForTests(ProxyToVim):

    IS_REMOTE_SETUP_IS_FALSE = 0
    IS_REMOTE_SETUP_IS_TRUE = 1

    def __init__(self):
        self.log = StringIO()
        print(file=self.log)
        self.state = None

    def setState(self, state):
        self.state = state

    def _remote_expr(self, expr):
        result = None
        print("expr: %s" % expr, file=self.log)
        if self.state == self.IS_REMOTE_SETUP_IS_TRUE:
            result = '1'
        elif self.state == self.IS_REMOTE_SETUP_IS_FALSE:
            result = '0'
        print("return: %s" % repr(result), file=self.log)
        return result

    def _send(self, command):
        print("send: %s" % command, file=self.log)

    def logged(self):
        return self.log.getvalue()


class Config(object):

    def __init__(self):
        self.script = 'script'
        self.server_name = 'servername'
        self.port = 6666

config = Config()
