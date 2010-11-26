import socket
from vimpdb.config import getRawConfiguration

vim = None


def make(module):
    global vim
    vim = module
    return Controller()


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


def buffer_exist():
    for win in vim.windows:
        try:                 #FIXME: Error while new a unnamed buffer
            if '-vimpdb-' in win.buffer.name:
                return True
        except:
            pass
    return False


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

        if not buffer_exist():
            self.pdb_buffer = buffer_create()

        pdb_buffer = self.pdb_buffer
        pdb_buffer[:] = None

        for line in message:
            pdb_buffer.append(line)
        del pdb_buffer[0]

    def buffer_close(self):
        buffer_close()
