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
endfunction

function! PDB_GetCommand(feedback)
    let command = input(a:feedback . " Pdb:")
    return command
endfunction

function! PDB_ShowFileAtLine(filename, line)
    call PDB_MoveToDebugTab()
    call PDB_reset_original_map()
    execute "view " . a:filename
    execute "normal " . a:line . "ggz."
    setlocal cursorline
    call PDB_Map()
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
endfunction

function! PDB_Reset()
    call PDB_Command('pdb')
    call Pdb_exit()
endfunction

function! PDB_Quit()
    call PDB_Command('q')
    call Pdb_exit()
endfunction

function! PDB_Break()
    let line = line('.')
    let filename = expand('%:p')
    call PDB_Command("b " . filename . ":" . line)
endfunction

if !exists(":PDBNext")
  command! PDBNext :call PDB_Command("n")
endif
if !exists(":PDBQuit")
  command! PDBQuit :call PDB_Command("q")
endif
if !exists(":PDBStep")
  command! PDBStep :call PDB_Command("s")
endif
if !exists(":PDBReturn")
  command! PDBReturn :call PDB_Command("r")
endif
if !exists(":PDBContinue")
  command! PDBContinue :call PDB_Continue()
endif
if !exists(":PDBBreak")
  command! PDBBreak :call PDB_Break()
endif
if !exists(":PDBDown")
  command! PDBDown :call PDB_Command("d")
endif
if !exists(":PDBUp")
  command! PDBUp :call PDB_Command("u")
endif
if !exists(":PDBReset")
  command! PDBReset :call PDB_Reset()
endif
if !exists(":PDBArgs")
  command! PDBArgs :call PDB_Command("a")
endif
if !exists("PDBWord")
  command! PDBWord :call PDB_Command("!".expand("<cword>"))
endif  

let s:pdb_map = {}
let s:pdb_map["n"] = "PDBNext"
let s:pdb_map["s"] = "PDBStep"
let s:pdb_map["c"] = "PDBContinue"
let s:pdb_map["q"] = "PDBQuit"
let s:pdb_map["d"] = "PDBDown"
let s:pdb_map["u"] = "PDBUp"
let s:pdb_map["r"] = "PDBReturn"
let s:pdb_map["x"] = "PDBReset"
let s:pdb_map["a"] = "PDBArgs"
let s:pdb_map["w"] = "PDBWord"
let s:pdb_map["b"] = "PDBBreak"

function! PDB_Map()
    if !exists("b:pdb_mapped")
        let b:pdb_mapped = 0
    endif
    if ! b:pdb_mapped
        call PDB_store_original_map()
        for key in keys(s:pdb_map)
            let command = s:pdb_map[key]
            execute "nmap <buffer> " . key . " :" . command . "<CR>"
        endfor
        let b:pdb_mapped = 1
    endif
endfunction

function! PDB_store_original_map()
    let b:pdb_original_map = {}
    for key in keys(s:pdb_map)
        let b:pdb_original_map[key] = maparg(key, "@n")
    endfor
endfunction

function! PDB_reset_original_map()
    if exists("b:pdb_mapped")
        if b:pdb_mapped
            for key in keys(b:pdb_original_map)
                execute "unmap <buffer> " . key 
                let value = b:pdb_original_map[key]
                if value != ""
                    execute "nmap <buffer> " . key . " " . value
                endif
            endfor
            let b:pdb_mapped = 0
        endif
    endif
endfunction
"---------------------------------------------------------------------
" PDB Exit
function! Pdb_exit()
    call Pdb_comm_deinit()
    call PDB_reset_original_map()
python <<EOT
vimpdb_buffer_write(["Switch back to shell."])   
EOT
endfunction


call PDB_Init()
