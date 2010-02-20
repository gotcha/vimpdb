
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

call PDB_MoveToDebugTab()

function! PDB_GetCommand(feedback)
    let command = input(a:feedback . " Pdb:")
    return command
endfunction

function! PDB_Command(command)
    python << EOF
import urllib2
cmd = vim.eval("a:command")
urllib2.urlopen('http://localhost:8000/?pdbcmd=%s' % cmd)
EOF
endfunction

function! PDB_SwitchBack()
    echo "Switch back to shell."   
endfunction

function! PDB_Continue()
    call PDB_Command('c')
    call PDB_SwitchBack()
endfunction

function! PDB_Reset()
    call PDB_Command('novim')
    call PDB_SwitchBack()
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

noremap <buffer><silent> n :PDBNext<CR>
noremap <buffer><silent> s :PDBStep<CR>
noremap <buffer><silent> c :PDBContinue<CR>
noremap <buffer><silent> q :PDBQuit<CR>
noremap <buffer><silent> d :PDBDown<CR>
noremap <buffer><silent> u :PDBUp<CR>
noremap <buffer><silent> r :PDBReturn<CR>
noremap <buffer><silent> x :PDBReset<CR>
