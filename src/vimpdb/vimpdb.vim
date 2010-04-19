function! PDB_init_display()
    call PDB_move_to_debug_tab()
    " avoid "Press Enter to continue"
    execute "set cmdheight=2"
    call foreground()
endfunction

function! PDB_show_file_at_line(filename, line)
    call PDB_init_display()
    call PDB_reset_original_map()
    execute "view " . a:filename
    execute "normal " . a:line . "ggz."
    setlocal cursorline
    call PDB_map()
endfunction

function! PDB_show_feedback(message)
    call PDB_init_display()
python <<EOT
_message = vim.eval("a:message")
vimpdb_buffer_write(_message)
EOT
endfunction

"---------------------------------------------------------------------
" debug tab support
"
" We use a separate debug tab.
function! s:PDB_create_debug_tab()
    execute "tabnew"
    let t:vimpdb = "vimpdb"
endfunction

function! PDB_move_to_debug_tab()
    for i in range(tabpagenr('$'))
        exe i+1 "tabnext"
        if exists("t:vimpdb") == 1
            return
        endif
    endfor
    call s:PDB_create_debug_tab()
endfunction

"---------------------------------------------------------------------
" vim to pdb communication
function! PDB_send_command(command)
python <<EOT
_command = vim.eval("a:command")
vimpdb_socket_send(_command)
EOT
endfunction

python <<EOT
import socket

def vimpdb_socket_get():
    try:
        return socket_to_pdb
    except NameError:
        socket_to_pdb = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        return socket_to_pdb

def vimpdb_socket_send(message):
    PDB_ADDRESS = '127.0.0.1'
    PDB_PORT = 6666
    send_socket = vimpdb_socket_get()
    send_socket.sendto(message, (PDB_ADDRESS, PDB_PORT))

def vimpdb_socket_close():
    try:
        socket_to_pdb.close()
        del socket_to_pdb
    except NameError:
        pass

#---------------------------------------------------------------------
# vimpdb feedback buffer
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
    vim.command('silent rightbelow 5new -vimpdb-')
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
    vim.command('silent! bwipeout -vimpdb-')

def vimpdb_buffer_exist():
    for win in vim.windows:
        try:                 #FIXME: Error while new a unnamed buffer
            if '-vimpdb-' in win.buffer.name:
                return True
        except: pass
    return False
EOT

"---------------------------------------------------------------------
" Keyboard mapping management
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

function! PDB_map()
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
        let b:pdb_original_map[key] = maparg(key, "n")
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
" code leftover from hacking period
function! PDB_get_command(feedback)
    let command = input(a:feedback . " Pdb:")
    return command
endfunction

"---------------------------------------------------------------------
" ex mode commands support
function! PDB_continue()
    call PDB_send_command('c')
    call PDB_reset_original_map()
endfunction

function! PDB_reset()
    call PDB_send_command('pdb')
    call PDB_exit()
endfunction

function! PDB_quit()
    call PDB_send_command('q')
    call PDB_exit()
endfunction

function! PDB_break()
    let line = line('.')
    let filename = expand('%:p')
    call PDB_send_command("b " . filename . ":" . line)
endfunction

function! PDB_exit()
    call PDB_reset_original_map()
python <<EOT
vimpdb_socket_close()
vimpdb_buffer_write(["Switch back to shell."])   
EOT
endfunction

"---------------------------------------------------------------------
" ex mode commands
if !exists(":PDBNext")
  command! PDBNext :call PDB_send_command("n")
endif
if !exists(":PDBQuit")
  command! PDBQuit :call PDB_quit()
endif
if !exists(":PDBStep")
  command! PDBStep :call PDB_send_command("s")
endif
if !exists(":PDBReturn")
  command! PDBReturn :call PDB_send_command("r")
endif
if !exists(":PDBContinue")
  command! PDBContinue :call PDB_continue()
endif
if !exists(":PDBBreak")
  command! PDBBreak :call PDB_break()
endif
if !exists(":PDBDown")
  command! PDBDown :call PDB_send_command("d")
endif
if !exists(":PDBUp")
  command! PDBUp :call PDB_send_command("u")
endif
if !exists(":PDBReset")
  command! PDBReset :call PDB_reset()
endif
if !exists(":PDBArgs")
  command! PDBArgs :call PDB_send_command("a")
endif
if !exists("PDBWord")
  command! PDBWord :call PDB_send_command("!".expand("<cword>"))
endif  
