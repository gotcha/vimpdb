import os
from mock import Mock


def test_ProxyToVim_instantiation():
    from vimpdb.proxy import ProxyToVim

    communicator = Mock(spec=['_remote_expr', '_send'])

    to_vim = ProxyToVim(communicator)
    assert isinstance(to_vim, ProxyToVim)


def test_ProxyToVim_setupRemote():
    from vimpdb.proxy import ProxyToVim

    communicator = Mock(spec=['_remote_expr', '_send'])
    communicator._remote_expr.return_value = '0'

    to_vim = ProxyToVim(communicator)
    to_vim.setupRemote()

    method_calls = communicator.method_calls
    assert len(method_calls) == 5
    call = method_calls[0]
    assert call[0] == '_remote_expr'
    assert call[1] == ("exists('*PDB_setup_egg')",)
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
    call = method_calls[0]
    assert call[0] == '_remote_expr'
    assert call[1] == ("exists('*PDB_setup_egg')",)


def test_ProxyToVim_isRemoteSetup():
    from vimpdb.proxy import ProxyToVim

    communicator = Mock(spec=['_remote_expr', '_send'])

    to_vim = ProxyToVim(communicator)
    to_vim.isRemoteSetup()

    method_calls = communicator.method_calls
    assert len(method_calls) == 1
    call = method_calls[0]
    assert call[0] == '_remote_expr'
    assert call[1] == ("exists('*PDB_setup_egg')",)


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
    call = method_calls[0]
    assert call[0] == '_remote_expr'
    assert call[1] == ("exists('*PDB_setup_egg')",)
    call = method_calls[1]
    assert call[0] == '_send'
    assert call[1][0] == ":call PDB_show_feedback(['first', 'second'])<CR>"


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

    method_calls = communicator.method_calls
    assert len(method_calls) == 2
    call = method_calls[0]
    assert call[0] == '_remote_expr'
    assert call[1] == ("exists('*PDB_setup_egg')",)
    call = method_calls[1]
    assert call[0] == '_send'
    assert call[1][0].startswith(':call PDB_show_file_at_line("')
    assert call[1][0].endswith(' "1")<CR>')
    assert not '\\' in call[1][0]


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
    call = method_calls[0]
    assert call[0] == '_remote_expr'
    assert call[1] == ("exists('*PDB_setup_egg')",)
    call = method_calls[1]
    assert call[0] == '_send'
    assert call[1][0].startswith(':call PDB_show_file_at_line("')
    assert call[1][0].endswith(' "1")<CR>')
    assert not '\\' in call[1][0]


def test_ProxyFromVim_instantiation():
    from vimpdb.proxy import ProxyFromVim
    from_vim = ProxyFromVim(6666)
    assert isinstance(from_vim, ProxyFromVim)
