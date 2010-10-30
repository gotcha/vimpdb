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
    detect.check_serverlist()


def test_detect_wrongserverlist():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('wrongserverlist.py')
    config = Config(script=script)
    detect = Detector(config)
    assert 'WRONG' in detect.get_serverlist()
    py.test.raises(ValueError, detect.check_serverlist)


def test_detector_instantiation():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    config = Config()
    detector = Detector(config)
    assert detector.port == config.port
    assert detector.script == config.script
    assert detector.server_name == config.server_name


def test_detector_build_command():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    config = Config()
    detector = Detector(config)
    result = detector.build_command("test")
    assert result[-1] == "test"
    assert result[0:-1] == config.script.split()


def test_detector_get_vim_version_bad_script():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    config = Config()
    detector = Detector(config)
    info = py.test.raises(ValueError, detector.get_vim_version)
    assert (info.value.args[0] ==
        "'script --version' returned exit code '1'.")


def test_detector_get_vim_version_good_script():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('compatiblevim.py')
    config = Config(script=script)
    detector = Detector(config)
    version = detector.get_vim_version()
    assert version == '+clientserver +python'


def test_detector_check_python_support():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('compatiblevim.py')
    config = Config(script=script)
    detector = Detector(config)
    assert detector.check_python_support()


def test_detector_no_python_support():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('nopython.py')
    config = Config(script=script)
    detector = Detector(config)
    info = py.test.raises(ValueError, detector.check_python_support)
    assert info.value.args[0].endswith(
        "' launches a VIM instance without python support.")


def test_detector_no_python_in_version():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('rightserverlist.py')
    config = Config(script=script)
    detector = Detector(config)
    info = py.test.raises(ValueError, detector.check_python_support)
    assert (info.value.args[0] ==
      'Calling --version returned no information about python support:\n VIM')


def test_detector_check_server_support():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('compatiblevim.py')
    config = Config(script=script)
    detector = Detector(config)
    assert detector.check_server_support()


def test_detector_no_server_support():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('noserver.py')
    config = Config(script=script)
    detector = Detector(config)
    info = py.test.raises(ValueError, detector.check_server_support)
    assert info.value.args[0].endswith(
        "' launches a VIM instance without server support.")


def test_detector_no_clientserver_in_version():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('rightserverlist.py')
    config = Config(script=script)
    detector = Detector(config)
    info = py.test.raises(ValueError, detector.check_server_support)
    assert (info.value.args[0] ==
        ('Calling --version returned no information about clientserver '
        'support:\n VIM'))


def test_detector_get_serverlist():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('rightserverlist.py')
    config = Config(script=script)
    detector = Detector(config)
    serverlist = detector.get_serverlist()
    assert serverlist == "VIM"


def test_detector_get_serverlist_bad_script():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    config = Config()
    detector = Detector(config)
    info = py.test.raises(ValueError, detector.get_serverlist)
    assert (info.value.args[0] ==
        "'script --serverlist' returned exit code '1'.")


def test_detector_check_serverlist():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('rightserverlist.py')
    config = Config(script=script, server_name='VIM')
    detector = Detector(config)
    assert detector.check_serverlist()


def test_detector_server_not_available():
    from vimpdb.config import Detector
    from vimpdb.testing import Config
    script = build_script('rightserverlist.py')
    config = Config(script=script, server_name="SERVERNAME")
    detector = Detector(config)
    info = py.test.raises(ValueError, detector.check_serverlist)
    assert (info.value.args[0] ==
        "'SERVERNAME' server name not available in server list:\nVIM")


def test_detector_launch_bad_script():
    from vimpdb.config import Detector
    from vimpdb.config import ReturnCodeError
    from vimpdb.testing import Config
    config = Config(server_name="VIM")
    detector = Detector(config)
    info = py.test.raises(ReturnCodeError, detector.launch_vim_server)
    assert info.value.args[0] == 1
    assert info.value.args[1] == 'script --servername VIM'


if __name__ == '__main__':
    test_detector_get_vim_version_good_script()
