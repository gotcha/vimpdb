import os
import sys
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


def build_script(script):
    from vimpdb.proxy import getPackagePath
    tests_path = getPackagePath(build_script)
    script_path = sys.executable + " " + os.path.sep.join([tests_path,
        'scripts', script])
    return script_path


def test_detect_compatible():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('compatiblevim.py')
    config = Config(script=script)
    detect = Detector(config)
    detect.check_server_support()
    detect.check_python_support()


def test_detect_incompatible():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('incompatiblevim.py')
    config = Config(script=script)
    detect = Detector(config)
    py.test.raises(ValueError, detect.check_server_support)
    py.test.raises(ValueError, detect.check_python_support)


def test_detect_rightserverlist():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('rightserverlist.py')
    config = Config(script=script, server_name="VIM")
    detect = Detector(config)
    assert 'VIM' in detect.get_serverlist()
    assert 'VIM' == detect.server_name
    detect.check_serverlist()


def test_detect_wrongserverlist():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('wrongserverlist.py')
    config = Config(script=script)
    detect = Detector(config)
    assert 'WRONG' in detect.get_serverlist()
    py.test.raises(ValueError, detect.check_serverlist)
