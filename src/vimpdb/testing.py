from proxy import ProxyToVim
from StringIO import StringIO


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
