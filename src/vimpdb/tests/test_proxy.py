def test_ProxyToVim_instantiation():
    from vimpdb.proxy import ProxyToVim
    to_vim = ProxyToVim()
    assert isinstance(to_vim, ProxyToVim)


def test_ProxyToVim_setupRemote():
    from vimpdb.testing import ProxyToVimForTests
    to_vim = ProxyToVimForTests()
    to_vim.setState(to_vim.IS_REMOTE_SETUP_IS_FALSE)
    to_vim.setupRemote()
    lines = to_vim.logged().splitlines()
    assert len(lines) == 4
    assert lines[1] == "expr: exists('*PDB_init')"
    assert lines[2] == "return: '0'"
    assert lines[3].startswith('send: <C-\\><C-N>:source ')
    assert lines[3].endswith('vimpdb/vimpdb.vim<CR>')


def test_ProxyToVim_setupRemote_does_nothing():
    from vimpdb.testing import ProxyToVimForTests
    to_vim = ProxyToVimForTests()
    to_vim.setState(to_vim.IS_REMOTE_SETUP_IS_TRUE)
    to_vim.setupRemote()
    assert (to_vim.logged() ==
"""
expr: exists('*PDB_init')
return: '1'
""")


def test_ProxyToVim_isRemoteSetup():
    from vimpdb.testing import ProxyToVimForTests
    to_vim = ProxyToVimForTests()
    to_vim.isRemoteSetup()
    assert (to_vim.logged() ==
"""
expr: exists('*PDB_init')
return: None
""")


def test_ProxyFromVim_instantiation():
    from vimpdb.proxy import ProxyFromVim
    from_vim = ProxyFromVim()
    assert isinstance(from_vim, ProxyFromVim)
