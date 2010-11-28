import os
import sys
import py


def test_read_options():
    import tempfile
    from vimpdb.config import CLIENT
    from vimpdb.config import SERVER
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
    from vimpdb.config import read_from_file
    from vimpdb.config import Config
    configuration = read_from_file(name, Config)
    assert configuration.port == 1000
    assert configuration.scripts[CLIENT] == 'vim_client_script'
    assert configuration.scripts[SERVER] == 'vim_server_script'
    assert configuration.server_name == 'server_name'
    os.remove(name)


def test_read_options_legacy_script():
    import tempfile
    from vimpdb.config import CLIENT
    from vimpdb.config import SERVER
    handle, name = tempfile.mkstemp()
    file = open(name, 'w')
    file.write("""
[vimpdb]
script = vim_client_script
port = 1000
server_name = server_name
""")
    file.close()
    from vimpdb.bbbconfig import read_from_file_4_0
    from vimpdb.config import Config
    configuration = read_from_file_4_0(name, Config)
    assert configuration.port == 1000
    assert configuration.scripts[CLIENT] == 'vim_client_script'
    assert configuration.scripts[SERVER] == 'vim_client_script'
    assert configuration.server_name == 'server_name'
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
    from vimpdb.errors import BadRCFile
    from vimpdb.config import read_from_file
    from vimpdb.config import Config
    py.test.raises(BadRCFile, read_from_file, name, Config)
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
    from vimpdb.errors import BadRCFile
    from vimpdb.config import read_from_file
    from vimpdb.config import Config
    py.test.raises(BadRCFile, read_from_file, name, Config)
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
    from vimpdb.errors import BadRCFile
    from vimpdb.config import read_from_file
    from vimpdb.config import Config
    py.test.raises(BadRCFile, read_from_file, name, Config)
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
    from vimpdb.errors import BadRCFile
    from vimpdb.config import read_from_file
    from vimpdb.config import Config
    py.test.raises(BadRCFile, read_from_file, name, Config)
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
    from vimpdb.errors import BadRCFile
    from vimpdb.config import read_from_file
    from vimpdb.config import Config
    py.test.raises(BadRCFile, read_from_file, name, Config)
    os.remove(name)


def test_default_config():
    from vimpdb.config import CLIENT
    from vimpdb.config import SERVER
    from vimpdb.config import defaultConfig
    from vimpdb.config import DEFAULT_PORT
    from vimpdb.config import DEFAULT_CLIENT_SCRIPT
    from vimpdb.config import DEFAULT_SERVER_SCRIPT
    from vimpdb.config import DEFAULT_SERVER_NAME
    configuration = defaultConfig
    assert configuration.port == DEFAULT_PORT
    assert configuration.scripts[CLIENT] == DEFAULT_CLIENT_SCRIPT
    assert configuration.scripts[SERVER] == DEFAULT_SERVER_SCRIPT
    assert configuration.server_name == DEFAULT_SERVER_NAME


def test_file_creation():
    import tempfile
    handle, name = tempfile.mkstemp()
    os.remove(name)
    from vimpdb.config import defaultConfig
    from vimpdb.config import DEFAULT_PORT
    from vimpdb.config import DEFAULT_CLIENT_SCRIPT
    from vimpdb.config import DEFAULT_SERVER_SCRIPT
    from vimpdb.config import DEFAULT_SERVER_NAME
    from vimpdb.config import write_to_file
    write_to_file(name, defaultConfig)
    assert os.path.exists(name)
    config_file = open(name)
    content = config_file.read()
    assert 'vim_client_script =' in content
    assert DEFAULT_CLIENT_SCRIPT in content
    assert 'vim_server_script =' in content
    assert DEFAULT_SERVER_SCRIPT in content
    assert 'port =' in content
    assert str(DEFAULT_PORT) in content
    assert 'server_name =' in content
    assert DEFAULT_SERVER_NAME in content
    config_file.close()
    os.remove(name)


def build_script(vim_client_script):
    """make path to scripts used by tests
    """

    from vimpdb.config import get_package_path
    tests_path = get_package_path(build_script)
    script_path = sys.executable + " " + os.path.sep.join([tests_path,
        'scripts', vim_client_script])
    return script_path


def makeDetector(**kwargs):
    """ make detector from configuration built with args rather
    than by reading config file
    """

    from vimpdb.config import Detector
    from vimpdb.config import Config
    if "vim_client_script" in kwargs:
        vim_client_script = build_script(kwargs["vim_client_script"])
    else:
        vim_client_script = None
    if "vim_server_script" in kwargs:
        vim_server_script = build_script(kwargs["vim_server_script"])
    else:
        vim_server_script = build_script('server_script')
    if "server_name" in kwargs:
        server_name = kwargs["server_name"]
    else:
        server_name = 'server_name'
    if "port" in kwargs:
        port = kwargs["port"]
    else:
        port = 6666
    configuration = Config(vim_client_script=vim_client_script,
        vim_server_script=vim_server_script, server_name=server_name,
        port=port)
    detector = Detector(configuration)
    detector.MAX_TIMEOUT = 0.5
    return detector


def test_detect_compatible():
    from vimpdb import config

    vim_client_script = build_script("compatiblevim.py")
    vim_server_script = build_script("compatiblevim.py")
    server_name = 'server_name'
    port = 6666

    configuration = config.Config(vim_client_script, vim_server_script,
        server_name, port)

    detector = config.Detector(configuration)
    detector.check_clientserver_support(config.SERVER)
    detector.check_clientserver_support(config.CLIENT)
    detector.check_python_support()


def test_detect_incompatible():
    from vimpdb import config

    vim_client_script = "dummy"
    vim_server_script = build_script("incompatiblevim.py")
    server_name = 'server_name'
    port = 6666

    configuration = config.Config(vim_client_script, vim_server_script,
        server_name, port)

    detector = config.Detector(configuration)
    py.test.raises(ValueError, detector.check_clientserver_support,
        config.SERVER)
    py.test.raises(ValueError, detector.check_python_support)


def test_detect_rightserverlist():
    from vimpdb import config

    vim_client_script = build_script("rightserverlist.py")
    vim_server_script = "dummy"
    server_name = 'VIM'
    port = 6666

    configuration = config.Config(vim_client_script, vim_server_script,
        server_name, port)

    detector = config.Detector(configuration)
    assert 'VIM' in detector.get_serverlist()
    detector.check_serverlist()


def test_detect_wrongserverlist():
    from vimpdb import config

    vim_client_script = build_script("wrongserverlist.py")
    vim_server_script = "dummy"
    server_name = 'VIM'
    port = 6666

    configuration = config.Config(vim_client_script, vim_server_script,
        server_name, port)

    detector = config.Detector(configuration)
    assert 'WRONG' in detector.get_serverlist()
    py.test.raises(ValueError, detector.check_serverlist)


def test_detector_instantiation():
    from vimpdb.config import Detector
    from vimpdb.config import SERVER
    from vimpdb.config import CLIENT
    from vimpdb.config import Config
    configuration = Config('vim_client_script', 'vim_server_script',
        'server_name', 6666)
    detector = Detector(configuration)
    assert detector.port == configuration.port
    assert detector.scripts[CLIENT] == configuration.scripts[CLIENT]
    assert detector.scripts[SERVER] == configuration.scripts[SERVER]
    assert detector.server_name == configuration.server_name


def test_detector_build_command():
    from vimpdb.config import Detector
    from vimpdb.config import CLIENT
    from vimpdb.config import Config
    configuration = Config('vim_client_script', 'vim_server_script',
        'server_name', 6666)
    detector = Detector(configuration)
    result = detector.build_command(CLIENT, "test")
    assert result[-1] == "test"
    assert result[0:-1] == configuration.scripts[CLIENT].split()


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
    detector = makeDetector(vim_server_script='compatiblevim.py')
    assert detector.check_python_support()


def test_detector_no_python_support():
    detector = makeDetector(vim_server_script='nopython.py')
    info = py.test.raises(ValueError, detector.check_python_support)
    assert info.value.args[0].endswith(
        "' launches a VIM instance without python support.")


def test_detector_no_python_in_version():
    detector = makeDetector(vim_server_script='rightserverlist.py')
    info = py.test.raises(ValueError, detector.check_python_support)
    assert (info.value.args[0] ==
      'Calling --version returned no information about python support:\n VIM')


def test_detector_check_clientserver_support():
    from vimpdb.config import CLIENT
    detector = makeDetector(vim_client_script='compatiblevim.py')
    assert detector.check_clientserver_support(CLIENT)


def test_detector_no_clientserver_support():
    from vimpdb.config import CLIENT
    detector = makeDetector(vim_client_script='noserver.py')
    info = py.test.raises(ValueError, detector.check_clientserver_support,
        CLIENT)
    assert info.value.args[0].endswith(
        "' launches a VIM instance without clientserver support.")


def test_detector_no_clientserver_in_version():
    from vimpdb.config import CLIENT
    detector = makeDetector(vim_client_script='rightserverlist.py')
    info = py.test.raises(ValueError, detector.check_clientserver_support,
        CLIENT)
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


def test_detector_check_serverlist_bad_server_script():
    detector = makeDetector(vim_client_script='emptyserverlist.py',
        vim_server_script='returncode.py', server_name='VIM')
    info = py.test.raises(ValueError, detector.check_serverlist)
    assert (info.value.args[0].endswith(
        "returncode.py --servername VIM' returned exit code '1'."))


def test_detector_server_not_available():
    detector = makeDetector(vim_client_script="rightserverlist.py",
        vim_server_script="rightserverlist.py", server_name="SERVERNAME")
    info = py.test.raises(ValueError, detector.check_serverlist)
    assert (info.value.args[0] ==
        "'SERVERNAME' server name not available in server list:\nVIM")


def test_detector_launch_server():
    detector = makeDetector(vim_client_script="compatiblevim.py",
        vim_server_script="compatiblevim.py", server_name="VIM")
    assert detector.launch_vim_server()


def test_detector_launch_server_bad_script():
    from vimpdb import errors
    detector = makeDetector(vim_client_script="compatiblevim.py",
        vim_server_script="returncode.py", server_name="VIM")
    info = py.test.raises(errors.ReturnCodeError, detector.launch_vim_server)
    assert info.value.args[0] == 1
    assert info.value.args[1].endswith('returncode.py --servername VIM')


if __name__ == '__main__':
    test_detector_get_vim_version_good_script()
