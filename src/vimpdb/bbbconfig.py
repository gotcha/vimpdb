import os
import ConfigParser

from vimpdb import errors


def read_from_file_4_0(filename, klass):
    parser = ConfigParser.RawConfigParser()
    parser.read(filename)
    if not parser.has_section('vimpdb'):
        raise errors.BadRCFile('[vimpdb] section is missing in "%s"' %
            filename)
    error_msg = ("'%s' option is missing from section [vimpdb] in "
        + "'" + filename + "'.")
    if parser.has_option('vimpdb', 'script'):
        vim_client_script = parser.get('vimpdb', 'script')
    else:
        raise errors.BadRCFile(error_msg % "vim_client_script")
    if parser.has_option('vimpdb', 'server_name'):
        server_name = parser.get('vimpdb', 'server_name')
    else:
        raise errors.BadRCFile(error_msg % 'server_name')
    if parser.has_option('vimpdb', 'port'):
        port = parser.getint('vimpdb', 'port')
    else:
        raise errors.BadRCFile(error_msg % 'port')
    if parser.has_option('vimpdb', 'script'):
        vim_server_script = parser.get('vimpdb', 'script')
    else:
        raise errors.BadRCFile(error_msg % "vim_server_script")
    return klass(vim_client_script, vim_server_script, server_name, port)


ENVIRON_SCRIPT_KEY = "VIMPDB_VIMSCRIPT"
ENVIRON_SERVER_NAME_KEY = "VIMPDB_SERVERNAME"


def has_environ():
    return (ENVIRON_SERVER_NAME_KEY in os.environ) or (
        ENVIRON_SERVER_NAME_KEY in os.environ)


def read_from_environ(klass, default):
    script = os.environ.get(ENVIRON_SCRIPT_KEY, default.vim_client_script)
    server_name = os.environ.get(ENVIRON_SERVER_NAME_KEY, default.server_name)
    config = klass(script, script, server_name, default.port)
    return config
