import pdb
from pdb import Pdb
import sys
import StringIO
from vimpdb import proxy
from vimpdb import config

PYTHON_25_OR_BIGGER = sys.version_info >= (2, 5)
PYTHON_26_OR_BIGGER = sys.version_info >= (2, 6)


def capture_sys_stdout(method):

    def decorated(self, line):
        self.capture_sys_stdout()
        result = method(self, line)
        self.stop_capture_sys_stdout()
        self.to_vim.showFeedback(self.pop_output())
        return result

    return decorated


def capture_self_stdout(method):

    def decorated(self, line):
        self.capture_self_stdout()
        result = method(self, line)
        self.stop_capture_self_stdout()
        self.to_vim.showFeedback(self.pop_output())
        return result

    return decorated


if PYTHON_25_OR_BIGGER:
    capture = capture_self_stdout
else:
    capture = capture_sys_stdout


def show_line(method):

    def decorated(self, line):
        result = method(self, line)
        self.showFileAtLine()
        return result

    return decorated


def close_socket(method):

    def decorated(self, line):
        self.from_vim.closeSocket()
        return method(self, line)

    return decorated


class Switcher:
    """
    Helper for switching from pdb to vimpdb
    and vice versa
    """

    def set_trace_without_step(self, frame):
        self.reset()
        while frame:
            frame.f_trace = self.trace_dispatch
            self.botframe = frame
            frame = frame.f_back
        sys.settrace(self.trace_dispatch)

    def update_state(self, other):
        self.stack = other.stack
        self.curindex = other.curindex
        self.curframe = other.curframe

    def has_gone_up(self):
        return self.curindex + 1 != len(self.stack)


class VimPdb(Pdb, Switcher):
    """
    debugger integrated with Vim
    """

    def __init__(self, to_vim, from_vim):
        Pdb.__init__(self)
        self.capturing = False
        self.to_vim = to_vim
        self.from_vim = from_vim
        self._textOutput = ''

    def trace_dispatch(self, frame, event, arg):
        """allow to switch to Pdb instance"""
        if hasattr(self, 'pdb'):
            return self.pdb.trace_dispatch(frame, event, arg)
        else:
            return Pdb.trace_dispatch(self, frame, event, arg)

    def execRcLines(self):
        pass

    def cmdloop(self):
        stop = None
        self.preloop()
        while not stop:
            line = self.from_vim.waitFor(self)
            line = self.precmd(line)
            stop = self.onecmd(line)
            stop = self.postcmd(stop, line)
        self.postloop()

    def preloop(self):
        filename, lineno = self.getFileAndLine()
        self.to_vim.showFileAtLine(filename, lineno)

    def getFileAndLine(self):
        frame, lineno = self.stack[self.curindex]
        filename = self.canonic(frame.f_code.co_filename)
        return filename, lineno

    def showFileAtLine(self):
        filename, lineno = self.getFileAndLine()
        self.to_vim.showFileAtLine(filename, lineno)

    # stdout captures to send back to Vim
    def capture_sys_stdout(self):
        self.stdout = sys.stdout
        sys.stdout = StringIO.StringIO()
        self.capturing = True

    def stop_capture_sys_stdout(self):
        if self.capturing:
            self.capturing = False
            self.push_output(sys.stdout.getvalue())
            sys.stdout = self.stdout

    # stdout captures to send back to Vim
    def capture_self_stdout(self):
        self.initial_stdout = self.stdout
        self.stdout = StringIO.StringIO()
        self.capturing = True

    def stop_capture_self_stdout(self):
        if self.capturing:
            self.capturing = False
            self.push_output(self.stdout.getvalue())
            self.stdout = self.initial_stdout

    def push_output(self, text):
        self._textOutput += text

    def pop_output(self):
        result = self._textOutput
        self._textOutput = ''
        return result

    def do_pdb(self, line):
        """
        'pdb' command:
        switches back to debugging with (almost) standard pdb.Pdb
        except for added 'vim' command.
        """
        self.from_vim.closeSocket()
        self.pdb = get_hooked_pdb()
        self.pdb.set_trace_without_step(self.botframe)
        if self.has_gone_up():
            self.pdb.update_state(self)
            self.pdb.print_current_stack_entry()
            self.pdb.cmdloop()
        else:
            self.pdb.interaction(self.curframe, None)
        return 1

    do_u = do_up = capture(show_line(Pdb.do_up))
    do_d = do_down = capture(show_line(Pdb.do_down))
    do_a = do_args = capture(Pdb.do_args)
    do_b = do_break = capture(Pdb.do_break)
    do_cl = do_clear = capture(Pdb.do_clear)
    do_c = do_continue = close_socket(Pdb.do_continue)

    @capture
    def print_stack_entry(self, frame_lineno, prompt_prefix=pdb.line_prefix):
        return Pdb.print_stack_entry(self, frame_lineno, prompt_prefix)

    def default(self, line):
        # first char should not be output (it is the '!' needed to escape)
        self.push_output(line[1:] + " = ")
        return Pdb.default(self, line)

if PYTHON_26_OR_BIGGER:
    VimPdb.default = capture_self_stdout(VimPdb.default)
else:
    VimPdb.default = capture_sys_stdout(VimPdb.default)


def make_instance():
    configuration = config.getConfiguration()
    communicator = proxy.Communicator(configuration.vim_client_script,
        configuration.server_name)
    to_vim = proxy.ProxyToVim(communicator)
    from_vim = proxy.ProxyFromVim(configuration.port)
    return VimPdb(to_vim, from_vim)


def set_trace():
    """
    can be called like pdb.set_trace()
    """
    instance = make_instance()
    instance.set_trace(sys._getframe().f_back)


# hook vimpdb  #
################


def trace_dispatch(self, frame, event, arg):
    """allow to switch to Vimpdb instance"""
    if hasattr(self, 'vimpdb'):
        return self.vimpdb.trace_dispatch(frame, event, arg)
    else:
        return self._orig_trace_dispatch(frame, event, arg)


class VimpdbSwitcher(Switcher):
    """
    with vim command
    """

    def do_vim(self, arg):
        """v(im)
    switch to debugging with vimpdb"""
        self.vimpdb = make_instance()
        self.vimpdb.set_trace_without_step(self.botframe)
        if self.has_gone_up():
            self.vimpdb.update_state(self)
            self.vimpdb.cmdloop()
        else:
            self.vimpdb.interaction(self.curframe, None)
        return 1

    do_v = do_vim

    def print_current_stack_entry(self):
        self.print_stack_entry(self.stack[self.curindex])


def hook(klass):
    """
    monkey-patch pdb.Pdb class

    adds a 'vim' (and 'v') command:
    it switches to debugging with vimpdb
    """

    def setupMethod(klass, method):
        name = method.__name__
        orig = getattr(klass, name)
        orig_attr = '_orig_' + name
        if not hasattr(klass, orig_attr):
            setattr(klass, '_orig_' + name, orig)
            setattr(klass, name, method)

    if not hasattr(klass, 'do_vim'):
        setupMethod(klass, trace_dispatch)
        klass.__bases__ += (VimpdbSwitcher, )


def get_hooked_pdb():
    hook(Pdb)
    debugger = Pdb()
    return debugger
