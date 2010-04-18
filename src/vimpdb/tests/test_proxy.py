def test_ProxyToVim_instantiation():
    from vimpdb.proxy import ProxyToVim
    to_vim = ProxyToVim()
    assert isinstance(to_vim, ProxyToVim)


def test_ProxyFromVim_instantiation():
    from vimpdb.proxy import ProxyFromVim
    from_vim = ProxyFromVim()
    assert isinstance(from_vim, ProxyFromVim)
