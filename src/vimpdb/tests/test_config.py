import os
import py


def test_read_options():
    import tempfile
    handle, name = tempfile.mkstemp()
    file = open(name, 'w')
    file.write("""
[vimpdb]
script = script
port = 1000
server_name = server_name
""")
    file.close()
    from vimpdb.config import Config
    config = Config(name)
    assert config.port == 1000
    assert config.script == 'script'
    assert config.server_name == 'server_name'
    os.remove(name)


def test_no_vimpdb_section():
    import tempfile
    handle, name = tempfile.mkstemp()
    file = open(name, 'w')
    file.write("""
[vimpdbx]
script = script
port = 1000
server_name = server_name
""")
    file.close()
    from vimpdb.config import Config
    from vimpdb.config import BadConfiguration
    py.test.raises(BadConfiguration, Config, name)
    os.remove(name)


def test_missing_script_option():
    import tempfile
    handle, name = tempfile.mkstemp()
    file = open(name, 'w')
    file.write("""
[vimpdb]
scriptx = script
port = 1000
server_name = server_name
""")
    file.close()
    from vimpdb.config import Config
    from vimpdb.config import BadConfiguration
    py.test.raises(BadConfiguration, Config, name)
    os.remove(name)


def test_missing_port_option():
    import tempfile
    handle, name = tempfile.mkstemp()
    file = open(name, 'w')
    file.write("""
[vimpdb]
script = script
portx = 1000
server_name = server_name
""")
    file.close()
    from vimpdb.config import Config
    from vimpdb.config import BadConfiguration
    py.test.raises(BadConfiguration, Config, name)
    os.remove(name)


def test_missing_server_name_option():
    import tempfile
    handle, name = tempfile.mkstemp()
    file = open(name, 'w')
    file.write("""
[vimpdb]
script = script
port = 1000
server_namex = server_name
""")
    file.close()
    from vimpdb.config import Config
    from vimpdb.config import BadConfiguration
    py.test.raises(BadConfiguration, Config, name)
    os.remove(name)


def test_file_creation():
    import tempfile
    handle, name = tempfile.mkstemp()
    os.remove(name)
    from vimpdb.config import Config
    from vimpdb.config import DEFAULT_PORT
    from vimpdb.config import DEFAULT_SCRIPT
    from vimpdb.config import DEFAULT_SERVERNAME
    config = Config(name)
    assert os.path.exists(name)
    assert config.port == DEFAULT_PORT
    assert config.script == DEFAULT_SCRIPT
    assert config.server_name == DEFAULT_SERVERNAME
    os.remove(name)
