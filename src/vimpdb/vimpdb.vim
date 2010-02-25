
function! s:PDB_CreateDebugTab()
    execute "tabnew"
    let t:vimpdbhook = "vimpdbhook"
endfunction

function! PDB_MoveToDebugTab()
    for i in range(tabpagenr('$'))
        exe i+1 "tabnext"
        if exists("t:vimpdbhook") == 1
            return
        endif
    endfor
    call s:PDB_CreateDebugTab()
endfunction

function! PDB_Init()
    call PDB_MoveToDebugTab()
    call Pdb_comm_init()
    call PDB_Map()
endfunction

function! PDB_GetCommand(feedback)
    let command = input(a:feedback . " Pdb:")
    return command
endfunction

"---------------------------------------------------------------------
" initialize PDB/Vim communication
function! Pdb_comm_init()
python <<EOT
import vim
import socket
 
PDB_SERVER_ADDRESS = '127.0.0.1'
PDB_SERVER_PORT = 6666
try:
    pdb_server.close()
except:
    pass
pdb_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
EOT
endfunction

"---------------------------------------------------------------------
" deinitialize PDB/vim communication
function! Pdb_comm_deinit()
python <<EOT
try:
    pdb_server.close()
except:
    pass
EOT
endfunction


"---------------------------------------------------------------------
" send a message to the PDB server
function! Pdb_send(message)
python <<EOT
_message = vim.eval("a:message")
pdb_server.sendto(_message, (PDB_SERVER_ADDRESS, PDB_SERVER_PORT))
EOT
endfunction

function! PDB_Command(command)
    call Pdb_send(a:command)
endfunction

python <<EOT
def vimpdb_buffer_write(message):

    if not vimpdb_buffer_exist():
        vimpdb_buffer_create()

    pdb_buffer[:] = None

    for line in message:
        pdb_buffer.append(line)
    del pdb_buffer[0]

    #from normal mode into insert mode
    y, x = vim.current.window.cursor
    if len(vim.current.line) > x + 1:
        vim.command('normal l')
        vim.command('startinsert')
    else:
        vim.command('startinsert!')

def vimpdb_buffer_create():
    global pdb_buffer
    source_buffer = vim.current.buffer.name
    vim.command('silent rightbelow 5new -PDBVim-')
    vim.command('set buftype=nofile')
    vim.command('set noswapfile')
    vim.command('set nonumber')
    vim.command('set nowrap')
    pdb_buffer = vim.current.buffer
    while True:
        vim.command('wincmd w')   #switch back window
        if source_buffer == vim.current.buffer.name:
            break

def vimpdb_buffer_close():
    vim.command('silent! bwipeout -PDBVim-')

def vimpdb_buffer_exist():
    for win in vim.windows:
        try:                 #FIXME: Error while new a unnamed buffer
            if 'PDBVim' in win.buffer.name:
                return True
        except: pass
    return False
EOT

function! PDB_Feedback(message)
python <<EOT
_message = vim.eval("a:message")
vimpdb_buffer_write(_message)
EOT
endfunction

function! PDB_Continue()
    call PDB_Command('c')
    call PDB_SwitchBack()
endfunction

function! PDB_Reset()
    call PDB_Command('pdb')
    call Pdb_exit()
endfunction

function! PDB_Quit()
    call PDB_Command('q')
    call Pdb_exit()
endfunction

if !exists(":PDBNext")
  command PDBNext :call PDB_Command("n")
endif
if !exists(":PDBQuit")
  command PDBQuit :call PDB_Command("q")
endif
if !exists(":PDBStep")
  command PDBStep :call PDB_Command("s")
endif
if !exists(":PDBReturn")
  command PDBReturn :call PDB_Command("r")
endif
if !exists(":PDBContinue")
  command PDBContinue :call PDB_Continue()
endif
if !exists(":PDBDown")
  command PDBDown :call PDB_Command("d")
endif
if !exists(":PDBUp")
  command PDBUp :call PDB_Command("u")
endif
if !exists(":PDBReset")
  command PDBReset :call PDB_Reset()
endif
if !exists(":PDBArgs")
  command PDBArgs :call PDB_Command("a")
endif

function! PDB_Map()
    noremap <buffer><silent> n :PDBNext<CR>
    noremap <buffer><silent> s :PDBStep<CR>
    noremap <buffer><silent> c :PDBContinue<CR>
    noremap <buffer><silent> q :PDBQuit<CR>
    noremap <buffer><silent> d :PDBDown<CR>
    noremap <buffer><silent> u :PDBUp<CR>
    noremap <buffer><silent> r :PDBReturn<CR>
    noremap <buffer><silent> x :PDBReset<CR>
    noremap <buffer><silent> a :PDBArgs<CR>
endfunction

"---------------------------------------------------------------------
" PDB Exit
function! Pdb_exit()
    call Pdb_comm_deinit()
python <<EOT
vimpdb_buffer_write(["Switch back to shell."])   
EOT
endfunction


call PDB_Init()
