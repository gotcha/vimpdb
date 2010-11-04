import os
import sys
import py


def test_read_options():
    import tempfile
    handle, name = tempfile.mkstemp()
    file = open(name, 'w')
    file.write("""
[vimpdb]
vim_client_script = vim_client_script
vim_server_script = vim_server_script
port = 1000
server_name = server_name
""")
    file.close()
    from vimpdb.config import Config
    config = Config(name)
    assert config.port == 1000
    assert config.vim_client_script == 'vim_client_script'
    assert config.vim_server_script == 'vim_server_script'
    assert config.server_name == 'server_name'
    os.remove(name)


def test_read_options_legacy_script():
    import tempfile
    handle, name = tempfile.mkstemp()
    file = open(name, 'w')
    file.write("""
[vimpdb]
script = vim_client_script
port = 1000
server_name = server_name
""")
    file.close()
    from vimpdb.config import Config
    config = Config(name)
    assert config.port == 1000
    assert config.vim_client_script == 'vim_client_script'
    assert config.vim_server_script == 'vim_client_script'
    assert config.server_name == 'server_name'
    os.remove(name)


def test_no_vimpdb_section():
    import tempfile
    handle, name = tempfile.mkstemp()
    file = open(name, 'w')
    file.write("""
[vimpdbx]
vim_client_script = vim_client_script
port = 1000
server_name = server_name
""")
    file.close()
    from vimpdb.config import Config
    from vimpdb.config import BadConfiguration
    py.test.raises(BadConfiguration, Config, name)
    os.remove(name)


def test_missing_client_script_option():
    import tempfile
    handle, name = tempfile.mkstemp()
    file = open(name, 'w')
    file.write("""
[vimpdb]
vim_server_script = vim_server_script
port = 1000
server_name = server_name
""")
    file.close()
    from vimpdb.config import Config
    from vimpdb.config import BadConfiguration
    py.test.raises(BadConfiguration, Config, name)
    os.remove(name)


def test_missing_server_script_option():
    import tempfile
    handle, name = tempfile.mkstemp()
    file = open(name, 'w')
    file.write("""
[vimpdb]
vim_client_script = vim_client_script
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
vim_client_script = vim_client_script
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
vim_client_script = vim_client_script
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
    from vimpdb.config import DEFAULT_CLIENT_SCRIPT
    from vimpdb.config import DEFAULT_SERVER_SCRIPT
    from vimpdb.config import DEFAULT_SERVER_NAME
    config = Config(name)
    assert os.path.exists(name)
    assert config.port == DEFAULT_PORT
    assert config.vim_client_script == DEFAULT_CLIENT_SCRIPT
    assert config.vim_server_script == DEFAULT_SERVER_SCRIPT
    assert config.server_name == DEFAULT_SERVER_NAME
    config_file = open(name)
    content = config_file.read()
    assert 'vim_client_script =' in content
    assert 'vim_server_script =' in content
    assert 'port =' in content
    assert 'server_name =' in content
    config_file.close()
    os.remove(name)


def build_script(vim_client_script):
    """make path to scripts used by tests
    """

    from vimpdb.proxy import getPackagePath
    tests_path = getPackagePath(build_script)
    script_path = sys.executable + " " + os.path.sep.join([tests_path,
        'scripts', vim_client_script])
    return script_path


def makeDetector(**kwargs):
    """ make detector from config built with args rather
    than by reading config file
    """

    from vimpdb.config import Detector
    from vimpdb.testing import Config
    if "vim_client_script" in kwargs:
        vim_client_script = build_script(kwargs["vim_client_script"])
        del kwargs["vim_client_script"]
    else:
        vim_client_script = None
    if "vim_server_script" in kwargs:
        vim_server_script = build_script(kwargs["vim_server_script"])
        del kwargs["vim_server_script"]
    else:
        vim_server_script = None
    config = Config(vim_client_script=vim_client_script,
        vim_server_script=vim_server_script, **kwargs)
    return Detector(config)


def test_detect_compatible():
    from vimpdb.config import SERVER
    from vimpdb.config import CLIENT
    detector = makeDetector(vim_client_script='compatiblevim.py',
    vim_server_script='compatiblevim.py')
    detector.check_server_support(SERVER)
    detector.check_server_support(CLIENT)
    detector.check_python_support()


def test_detect_incompatible():
    from vimpdb.config import SERVER
    detector = makeDetector(vim_server_script='incompatiblevim.py')
    py.test.raises(ValueError, detector.check_server_support, SERVER)
    py.test.raises(ValueError, detector.check_python_support)


def test_detect_rightserverlist():
    detector = makeDetector(vim_client_script='rightserverlist.py',
        server_name="VIM")
    assert 'VIM' in detector.get_serverlist()
    detector.check_serverlist()


def test_detect_wrongserverlist():
    detector = makeDetector(vim_client_script='wrongserverlist.py')
    assert 'WRONG' in detector.get_serverlist()
    py.test.raises(ValueError, detector.check_serverlist)


def test_detector_instantiation():
    from vimpdb.config import Detector
    from vimpdb.config import SERVER
    from vimpdb.config import CLIENT
    from vimpdb.testing import config
    detector = Detector(config)
    assert detector.port == config.port
    assert detector.scripts[CLIENT] == config.vim_client_script
    assert detector.scripts[SERVER] == config.vim_server_script
    assert detector.server_name == config.server_name


def test_detector_build_command():
    from vimpdb.config import Detector
    from vimpdb.config import CLIENT
    from vimpdb.testing import config
    detector = Detector(config)
    result = detector.build_command(CLIENT, "test")
    assert result[-1] == "test"
    assert result[0:-1] == config.vim_client_script.split()


def test_detector_get_vim_version_bad_script():
    from vimpdb.config import CLIENT
    detector = makeDetector(vim_client_script="returncode.py")
    info = py.test.raises(ValueError, detector.get_vim_version, CLIENT)
    assert (info.value.args[0].endswith(
        "returncode.py --version' returned exit code '1'."))


def test_detector_get_vim_version_good_script():
    from vimpdb.config import CLIENT
    detector = makeDetector(vim_client_script='compatiblevim.py')
    version = detector.get_vim_version(CLIENT)
    assert version == '+clientserver +python'


def test_detector_check_python_support():
    detector = makeDetector(vim_client_script='compatiblevim.py')
    assert detector.check_python_support()


def test_detector_no_python_support():
    detector = makeDetector(vim_client_script='nopython.py')
    info = py.test.raises(ValueError, detector.check_python_support)
    assert info.value.args[0].endswith(
        "' launches a VIM instance without python support.")


def test_detector_no_python_in_version():
    detector = makeDetector(vim_client_script='rightserverlist.py')
    info = py.test.raises(ValueError, detector.check_python_support)
    assert (info.value.args[0] ==
      'Calling --version returned no information about python support:\n VIM')


def test_detector_check_server_support():
    from vimpdb.config import CLIENT
    detector = makeDetector(vim_client_script='compatiblevim.py')
    assert detector.check_server_support(CLIENT)


def test_detector_no_server_support():
    from vimpdb.config import CLIENT
    detector = makeDetector(vim_client_script='noserver.py')
    info = py.test.raises(ValueError, detector.check_server_support, CLIENT)
    assert info.value.args[0].endswith(
        "' launches a VIM instance without server support.")


def test_detector_no_clientserver_in_version():
    from vimpdb.config import CLIENT
    detector = makeDetector(vim_client_script='rightserverlist.py')
    info = py.test.raises(ValueError, detector.check_server_support, CLIENT)
    assert (info.value.args[0] ==
        ('Calling --version returned no information about clientserver '
        'support:\n VIM'))


def test_detector_get_serverlist():
    detector = makeDetector(vim_client_script='rightserverlist.py')
    serverlist = detector.get_serverlist()
    assert serverlist == "VIM"


def test_detector_get_serverlist_bad_script():
    detector = makeDetector(vim_client_script="returncode.py")
    info = py.test.raises(ValueError, detector.get_serverlist)
    assert (info.value.args[0].endswith(
        "returncode.py --serverlist' returned exit code '1'."))


def test_detector_check_serverlist():
    detector = makeDetector(vim_client_script='rightserverlist.py',
        server_name='VIM')
    assert detector.check_serverlist()


def test_detector_server_not_available():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    vim_client_script = build_script('rightserverlist.py')
    config = Config(vim_client_script=vim_client_script,
        server_name="SERVERNAME")
    detector = Detector(config)
    info = py.test.raises(ValueError, detector.check_serverlist)
    assert (info.value.args[0] ==
        "'SERVERNAME' server name not available in server list:\nVIM")


def test_detector_launch_server():
    detector = makeDetector(vim_client_script="compatiblevim.py",
        vim_server_script="compatiblevim.py", server_name="VIM")
    assert detector.launch_vim_server()


def test_detector_launch_server_bad_script():
    from vimpdb.config import ReturnCodeError
    detector = makeDetector(vim_client_script="compatiblevim.py",
        vim_server_script="returncode.py", server_name="VIM")
    info = py.test.raises(ReturnCodeError, detector.launch_vim_server)
    assert info.value.args[0] == 1
    assert info.value.args[1].endswith('returncode.py --servername VIM')


if __name__ == '__main__':
    test_detector_get_vim_version_good_script()
