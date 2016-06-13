" Exit when already loaded (or "compatible" mode set)
if exists("g:coati_autoload_loaded") || &cp
    finish
endif

" Vars used by this script, don't change
let g:coati_autoload_loaded = 1

if !has('python')
	call coati#error("Error: Required vim compiled with +python")
	finish
endif

function! coati#get(option, ...)
    for l:scope in ['b', 'g', 'l', 's']
        if exists(l:scope . ':' . a:option)
            return eval(l:scope . ':' . a:option)
        endif
    endfor

    if a:0 > 0
        return a:1
    endif

    call coati#error('Invalid or undefined option: ' . a:option)
endfunction

function! coati#error(message)
    echohl Error | echomsg a:message | echohl None
endfunction

" Configuration
let g:coati_to_vim_port =
      \ get( g:, 'coati_to_vim_port', 6666 )

let g:vim_to_coati_port =
      \ get( g:, 'vim_to_coati_port', 6667 )

let g:coati_ip =
      \ get( g:, 'coati_ip', "localhost" )

let g:coati_autostart = 
      \ get( g:, 'coati_autostart', 0 )

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')


" Load Python script
if filereadable($VIMRUNTIME."/plugin/python/coati.py")
  pyfile $VIMRUNTIME/plugin/coati.py
elseif filereadable($HOME."/.vim/plugin/python/coati.py")
  pyfile $HOME/.vim/plugin/python/coati.py
else
  " when we use pathogen for instance
  let $CUR_DIRECTORY=escape(expand('<sfile>:p:h'), '\')

  if filereadable($CUR_DIRECTORY."/coati.py")
    pyfile $CUR_DIRECTORY/coati.py
  else
    call confirm('vdebug.vim: Unable to find coati.py. Place it in either your home vim directory or in the Vim runtime directory.', 'OK')
  endif
endif


function! coati#ShowSettings()
python << endPython
Coati.printSettings()
endPython
endfunction

function! coati#CoatiInit()
python << endPython
Coati.startServer()
endPython
endfunction

function! coati#CoatiShutdown()
python << endPython
Coati.stopServer()
endPython
endfunction

function! coati#ActivateToken()
python << endPython
Coati.SendActivateToken()
endPython
endfunction

function! coati#RestartServer()
python << endPython
Coati.restartServer()
endPython
endfunction

function! coati#UpdateBuffer()
python << endPython
Coati.updateBuffer()
endPython
endfunction

if has('python')
	augroup CoatiPlugin
		autocmd FocusGained,BufEnter	* :call coati#UpdateBuffer()
		autocmd VimLeavePre				* :call coati#CoatiShutdown()
	augroup END
endif

python coati = Coati()

if( coati#get("coati_autostart") )
	call coati#CoatiInit()
endif

