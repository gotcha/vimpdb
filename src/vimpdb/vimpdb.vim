highlight link PdbCurrentLine Cursor

function! PDB_setup_egg(path)
python <<EOT
import sys
import vim
egg_path = vim.eval("a:path")
if egg_path not in sys.path:
    sys.path.insert(0, egg_path)
EOT
endfunction

function! PDB_init_controller()
python <<EOT
from vimpdb.controller import initialize
import vim
initialize(vim)
EOT
endfunction

function! s:PDB_init_display()
    call PDB_move_to_debug_tab()
    " avoid "Press Enter to continue"
    set cmdheight=2
    call foreground()
endfunction

function! PDB_show_file_at_line(filename, line)
    call s:PDB_init_display()
    let current_filename = expand('%:p')
    if current_filename != a:filename
        call s:PDB_load_file(a:filename)
    endif
    "PDB_map needs to be called each time a file is showed
    "to take care of the case when debugging starts again
    "after c(ontinue)
    call s:PDB_map()
    execute "normal " . a:line . "ggz."
    execute 'match PdbCurrentLine /\%' . a:line . 'l\s*\zs.\+/'
endfunction

function! s:PDB_load_file(filename)
    call s:PDB_reset_original_map()
    execute "view " . a:filename
    setlocal cursorline
    highlight PdbCurrentLine
endfunction

function! PDB_show_feedback(message)
    call s:PDB_init_display()
    call s:PDBBufferWrite(a:message)
endfunction

"---------------------------------------------------------------------
" debug tab support
"
" We use a separate debug tab.
function! s:PDB_create_debug_tab()
    let filename = expand('%')
    if len(filename) != 0 || &modified
        tabnew
    endif
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
let s:pdb_map["B"] = "PDBClear"
let s:pdb_map["?"] = "PDBEval"

function! s:PDB_map()
    if !exists("b:pdb_mapped")
        let b:pdb_mapped = 0
    endif
    if ! b:pdb_mapped
        call s:PDB_store_original_map()
        for key in keys(s:pdb_map)
            let command = s:pdb_map[key]
            execute "nmap <buffer> " . key . " :" . command . "<CR>"
        endfor
        let b:pdb_mapped = 1
    endif
endfunction

function! s:PDB_store_original_map()
    let b:pdb_original_map = {}
    for key in keys(s:pdb_map)
        let b:pdb_original_map[key] = maparg(key, "n")
    endfor
endfunction

function! s:PDB_reset_original_map()
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
    call PDBSendCommand('c')
    call s:PDB_reset_original_map()
    call s:PDBBufferClose()
endfunction

function! PDB_reset()
    call PDBSendCommand('pdb')
    call PDB_exit()
endfunction

function! PDB_quit()
    call PDBSendCommand('q')
    call PDB_exit()
endfunction

function! PDB_eval()
    let expr = input("vimpdb - Type Python expression:")
    call PDBSendCommand("!" . expr)
endfunction

function! PDB_break()
    let line = line('.')
    let filename = expand('%:p')
    call PDBSendCommand("b " . filename . ":" . line)
endfunction

function! PDB_clear()
    let line = line('.')
    let filename = expand('%:p')
    call PDBSendCommand("cl " . filename . ":" . line)
endfunction

function! PDB_exit()
    call s:PDB_reset_original_map()
    call s:PDBBufferClose()
    call s:PDBSocketClose()
    echohl ErrorMsg
    echo "Switch back to shell.\n\n"
    echohl None
endfunction

"---------------------------------------------------------------------
" ex mode commands
if !exists(":PDBNext")
  command! PDBNext :call PDBSendCommand("n")
endif
if !exists(":PDBQuit")
  command! PDBQuit :call PDB_quit()
endif
if !exists(":PDBStep")
  command! PDBStep :call PDBSendCommand("s")
endif
if !exists(":PDBReturn")
  command! PDBReturn :call PDBSendCommand("r")
endif
if !exists(":PDBContinue")
  command! PDBContinue :call PDB_continue()
endif
if !exists(":PDBEval")
  command! PDBEval :call PDB_eval()
endif
if !exists(":PDBBreak")
  command! PDBBreak :call PDB_break()
endif
if !exists(":PDBClear")
  command! PDBClear :call PDB_clear()
endif
if !exists(":PDBDown")
  command! PDBDown :call PDBSendCommand("d")
endif
if !exists(":PDBUp")
  command! PDBUp :call PDBSendCommand("u")
endif
if !exists(":PDBReset")
  command! PDBReset :call PDB_reset()
endif
if !exists(":PDBArgs")
  command! PDBArgs :call PDBSendCommand("a")
endif
if !exists("PDBWord")
  command! PDBWord :call PDBSendCommand("!".expand("<cword>"))
endif  
