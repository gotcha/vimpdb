from mock import Mock
from mock import patch


def test_klass_after_setup_method():
    from vimpdb.debugger import setupMethod

    mocked_method = Mock(name='orig')

    class Klass:

        method = mocked_method

    new_method = Mock(name='new')
    new_method.__name__ = 'method'

    setupMethod(Klass, new_method)

    assert hasattr(Klass, '_orig_method')
    assert Klass._orig_method == mocked_method
    assert hasattr(Klass, 'method')
    assert Klass.method == new_method


def test_instance_of_klass_after_setup_method():
    from vimpdb.debugger import setupMethod

    mocked_method = Mock(name='orig')

    class Klass:

        method = mocked_method

    new_method = Mock(name='new')
    new_method.__name__ = 'method'

    setupMethod(Klass, new_method)
    instance = Klass()
    instance.method()

    assert new_method.called

    instance._orig_method()
    assert mocked_method.called


@patch('vimpdb.debugger.trace_dispatch')
def test_hook(mocked_trace_dispatch):
    from vimpdb.debugger import hook
    from vimpdb.debugger import SwitcherToVimpdb

    class Klass:

        def trace_dispatch(self):
            pass

    orig_trace_dispatch = Klass.trace_dispatch
    mocked_trace_dispatch.__name__ = 'trace_dispatch'

    hook(Klass)

    assert Klass._orig_trace_dispatch == orig_trace_dispatch
    assert SwitcherToVimpdb in Klass.__bases__
    assert Klass.trace_dispatch == mocked_trace_dispatch


@patch('vimpdb.debugger.setupMethod')
def test_hook_do_nothing(mocked_setupMethod):
    from vimpdb.debugger import hook
    from vimpdb.debugger import SwitcherToVimpdb

    class Klass:

        def do_vim(self):
            pass


    hook(Klass)

    assert not mocked_setupMethod.called
    assert SwitcherToVimpdb not in Klass.__bases__


@patch('vimpdb.debugger.trace_dispatch')
def test_get_hooked_pdb(mocked_trace_dispatch):
    from pdb import Pdb
    from vimpdb.debugger import get_hooked_pdb
    from vimpdb.debugger import SwitcherToVimpdb

    mocked_trace_dispatch.__name__ = 'trace_dispatch'

    debugger = get_hooked_pdb()

    assert isinstance(debugger, Pdb)
    assert isinstance(debugger, SwitcherToVimpdb)
    assert hasattr(debugger, 'do_vim')
    assert debugger.trace_dispatch == mocked_trace_dispatch


@patch('vimpdb.config.get_configuration')
def test_make_instance(mocked_get_configuration):
    from vimpdb.config import Config
    from vimpdb.debugger import make_instance
    from vimpdb.debugger import VimPdb

    mocked_get_configuration.return_value = Config(
        'client', 'server', 'name', 6666)

    instance = make_instance()

    assert isinstance(instance, VimPdb)
    assert instance.from_vim.port == 6666
    assert instance.to_vim.communicator.script == 'client'
    assert instance.to_vim.communicator.server_name == 'name'
