import socket

from vimpdb.config import getRawConfiguration

from vim_bridge import bridged

vim = None
controller = None


def initialize(module):
    global vim
    global controller
    vim = module
    controller = Controller()


def buffer_create():
    source_buffer = vim.current.buffer.name
    vim.command('silent rightbelow 5new -vimpdb-')
    vim.command('set buftype=nofile')
    vim.command('set noswapfile')
    vim.command('set nonumber')
    vim.command('set nowrap')
    buffer = vim.current.buffer
    while True:
        vim.command('wincmd w')   #switch back window
        if source_buffer == vim.current.buffer.name:
            break
    return buffer


def buffer_close():
    vim.command('silent! bwipeout -vimpdb-')


def buffer_find():
    for win in vim.windows:
        try:                 #FIXME: Error while new a unnamed buffer
            if '-vimpdb-' in win.buffer.name:
                return win.buffer
        except:
            pass
    return None


class Controller(object):

    def __init__(self):
        config = getRawConfiguration()
        self.port = config.port
        self.host = '127.0.0.1'
        self.socket = None

    def init_socket(self):
        if self.socket is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                socket.IPPROTO_UDP)

    def socket_send(self, message):
        self.init_socket()
        self.socket.sendto(message, (self.host, self.port))

    def socket_close(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def buffer_write(self, message):

        self.pdb_buffer = buffer_find()
        if self.pdb_buffer is None:
            self.pdb_buffer = buffer_create()

        pdb_buffer = self.pdb_buffer
        pdb_buffer[:] = None

        for line in message:
            pdb_buffer.append(line)
        del pdb_buffer[0]

    def buffer_close(self):
        buffer_close()


@bridged
def _PDB_buffer_write(message):
    controller.buffer_write(message)


@bridged
def _PDB_buffer_close():
    controller.buffer_close()


@bridged
def _PDB_send_command(message):
    controller.socket_send(message)


@bridged
def _PDB_socket_close():
    controller.socket_close()
