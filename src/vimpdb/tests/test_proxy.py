import os
import sys
import py
from mock import Mock


def build_script(script):
    """make path to scripts used by tests
    """

    from vimpdb.config import get_package_path
    tests_path = get_package_path(build_script)
    script_path = sys.executable + " " + os.path.sep.join([tests_path,
        'scripts', script])
    return script_path


def test_Communicator_instantiation():
    from vimpdb.proxy import Communicator

    communicator = Communicator('script', 'server_name')

    assert communicator.script == 'script'
    assert communicator.server_name == 'server_name'


def test_Communicator_remote_expr_ok():
    from vimpdb.proxy import Communicator
    script = build_script("communicator.py")

    communicator = Communicator(script, 'server_name')
    result = communicator._remote_expr('expr')

    assert 'expr' in result
    assert 'server_name' in result


def test_Communicator_remote_expr_return_code():
    from vimpdb.proxy import Communicator
    from vimpdb.errors import RemoteUnavailable
    script = build_script("returncode.py")

    communicator = Communicator(script, 'server_name')
    py.test.raises(RemoteUnavailable, communicator._remote_expr, 'expr')


def test_Communicator_send_ok():
    from vimpdb.proxy import Communicator
    script = build_script("communicator.py")

    communicator = Communicator(script, 'server_name')
    communicator._send('command')


def test_Communicator_send_return_code():
    from vimpdb.proxy import Communicator
    from vimpdb.errors import RemoteUnavailable
    script = build_script("returncode.py")

    communicator = Communicator(script, 'server_name')
    py.test.raises(RemoteUnavailable, communicator._send, 'command')


def test_ProxyToVim_instantiation():
    from vimpdb.proxy import ProxyToVim

    communicator = Mock()

    to_vim = ProxyToVim(communicator)
    assert isinstance(to_vim, ProxyToVim)
    assert to_vim.communicator == communicator


def test_ProxyToVim_setupRemote():
    from vimpdb.proxy import ProxyToVim

    communicator = Mock(spec=['_remote_expr', '_send'])
    communicator._remote_expr.return_value = '0'

    to_vim = ProxyToVim(communicator)
    to_vim.setupRemote()

    method_calls = communicator.method_calls
    assert len(method_calls) == 5
    communicator._remote_expr.assert_called_with("exists('*PDB_setup_egg')")
    call = method_calls[1]
    assert call[0] == '_send'
    assert call[1][0].endswith('vimpdb/vimpdb.vim<CR>')
    call = method_calls[2]
    assert call[0] == '_send'
    assert call[1][0].startswith(':call PDB_setup_egg(')
    call = method_calls[3]
    assert call[0] == '_send'
    assert call[1][0].startswith(':call PDB_setup_egg(')
    call = method_calls[4]
    assert call[0] == '_send'
    assert call[1][0].startswith(':call PDB_init_controller(')


def test_ProxyToVim_setupRemote_does_nothing():
    from vimpdb.proxy import ProxyToVim

    communicator = Mock(spec=['_remote_expr', '_send'])
    communicator._remote_expr.return_value = '1'

    to_vim = ProxyToVim(communicator)
    to_vim.setupRemote()

    method_calls = communicator.method_calls
    assert len(method_calls) == 1
    communicator._remote_expr.assert_called_with("exists('*PDB_setup_egg')")


def test_ProxyToVim_isRemoteSetup():
    from vimpdb.proxy import ProxyToVim

    communicator = Mock(spec=['_remote_expr', '_send'])

    to_vim = ProxyToVim(communicator)
    to_vim.isRemoteSetup()

    method_calls = communicator.method_calls
    assert len(method_calls) == 1
    communicator._remote_expr.assert_called_with("exists('*PDB_setup_egg')")


def test_ProxyToVim_showFeedback_empty():
    from vimpdb.proxy import ProxyToVim

    communicator = Mock(spec=['_remote_expr', '_send'])

    to_vim = ProxyToVim(communicator)
    to_vim.showFeedback('')

    method_calls = communicator.method_calls
    assert len(method_calls) == 0


def test_ProxyToVim_showFeedback_content():
    from vimpdb.proxy import ProxyToVim

    communicator = Mock(spec=['_remote_expr', '_send'])
    communicator._remote_expr.return_value = '1'

    to_vim = ProxyToVim(communicator)
    to_vim.showFeedback('first\nsecond')

    method_calls = communicator.method_calls
    assert len(method_calls) == 2
    communicator._remote_expr.assert_called_with("exists('*PDB_setup_egg')")
    communicator._send.assert_called_with(
        ":call PDB_show_feedback(['first', 'second'])<CR>")


def test_ProxyToVim_showFileAtLine_wrong_file():
    from vimpdb.proxy import ProxyToVim

    communicator = Mock(spec=['_remote_expr', '_send'])
    communicator._remote_expr.return_value = '1'

    to_vim = ProxyToVim(communicator)
    to_vim.showFileAtLine('bla.vim', 1)

    method_calls = communicator.method_calls
    assert len(method_calls) == 0


def test_ProxyToVim_showFileAtLine_existing_file():
    from vimpdb.proxy import ProxyToVim
    from vimpdb.config import get_package_path

    existingFile = get_package_path(
        test_ProxyToVim_showFileAtLine_existing_file)

    communicator = Mock(spec=['_remote_expr', '_send'])
    communicator._remote_expr.return_value = '1'

    to_vim = ProxyToVim(communicator)
    to_vim.showFileAtLine(existingFile, 1)

    communicator._remote_expr.assert_called_with("exists('*PDB_setup_egg')")
    assert communicator._send.call_count == 1
    call_args, call_kwargs = communicator._send.call_args
    assert call_args[0].startswith(':call PDB_show_file_at_line("')
    assert call_args[0].endswith(' "1")<CR>')
    assert not '\\' in call_args[0]


def test_ProxyToVim_showFileAtLine_existing_file_windows():
    from vimpdb.proxy import ProxyToVim
    from vimpdb.config import get_package_path

    existingFile = get_package_path(
        test_ProxyToVim_showFileAtLine_existing_file)
    existingFile = existingFile.replace(os.sep, '\\')

    communicator = Mock(spec=['_remote_expr', '_send'])
    communicator._remote_expr.return_value = '1'

    to_vim = ProxyToVim(communicator)
    to_vim._showFileAtLine(existingFile, 1)

    method_calls = communicator.method_calls
    assert len(method_calls) == 2
    communicator._remote_expr.assert_called_with("exists('*PDB_setup_egg')")
    call = method_calls[1]
    assert call[0] == '_send'
    assert call[1][0].startswith(':call PDB_show_file_at_line("')
    assert call[1][0].endswith(' "1")<CR>')
    assert not '\\' in call[1][0]


def test_ProxyFromVim_instantiation():
    from vimpdb.proxy import ProxyFromVim
    from_vim = ProxyFromVim(6666)
    assert isinstance(from_vim, ProxyFromVim)
    assert from_vim.port == 6666
    assert from_vim.socket_inactive


def test_ProxyFromVim_bindSocket():
    from vimpdb.proxy import ProxyFromVim
    from_vim = ProxyFromVim(6666)

    mocked_socket = Mock(spec=['bind'])
    mocked_factory = Mock(return_value=mocked_socket)
    from_vim.socket_factory = mocked_factory

    from_vim.bindSocket()

    assert not from_vim.socket_inactive
    method_calls = mocked_socket.method_calls
    assert len(method_calls) == 1
    call = method_calls[0]
    assert call[0] == 'bind'
    assert call[1] == (('', 6666),)


def test_ProxyFromVim_bindSocket_active():
    from vimpdb.proxy import ProxyFromVim
    from_vim = ProxyFromVim(6666)

    mocked_factory = Mock()
    from_vim.socket_factory = mocked_factory
    from_vim.socket_inactive = False

    from_vim.bindSocket()

    assert mocked_factory.call_count == 0


def test_ProxyFromVim_closeSocket():
    from vimpdb.proxy import ProxyFromVim
    from_vim = ProxyFromVim(6666)

    mocked_socket = Mock(spec=['close'])
    from_vim.socket = mocked_socket
    from_vim.socket_inactive = False

    from_vim.closeSocket()

    assert from_vim.socket_inactive
    method_calls = mocked_socket.method_calls
    assert len(method_calls) == 1
    call = method_calls[0]
    assert call[0] == 'close'


def test_ProxyFromVim_closeSocket_inactive():
    from vimpdb.proxy import ProxyFromVim
    from_vim = ProxyFromVim(6666)

    mocked_socket = Mock(spec=['close'])
    from_vim.socket = mocked_socket

    from_vim.closeSocket()

    assert from_vim.socket_inactive
    method_calls = mocked_socket.method_calls
    assert len(method_calls) == 0


def test_ProxyFromVim_waitFor():
    from vimpdb.proxy import ProxyFromVim
    from_vim = ProxyFromVim(6666)

    mocked_socket = Mock(spec=['bind', 'recvfrom'])
    mocked_socket.recvfrom.return_value = ('message', None)
    mocked_factory = Mock(return_value=mocked_socket)
    from_vim.socket_factory = mocked_factory

    message = from_vim.waitFor(None)

    assert message == 'message'
    method_calls = mocked_socket.method_calls
    assert len(method_calls) == 2
    call = method_calls[1]
    assert call[0] == 'recvfrom'
