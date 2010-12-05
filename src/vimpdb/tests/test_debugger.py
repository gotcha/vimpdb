from mock import Mock


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
