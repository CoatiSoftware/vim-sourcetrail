" Exit when already loaded (or "compatible" mode set)
if exists("g:sourcetrail_autoload_loaded") || &cp
    finish
endif

" Vars used by this script, don't change
let g:sourcetrail_autoload_loaded = 1

if !has('python')
	call sourcetrail#error("Error: Required vim compiled with +python")
	finish
endif


function! sourcetrail#get(option, ...)
    for l:scope in ['b', 'g', 'l', 's']
        if exists(l:scope . ':' . a:option)
            return eval(l:scope . ':' . a:option)
        endif
    endfor

    if a:0 > 0
        return a:1
    endif

    call sourcetrail#error('Invalid or undefined option: ' . a:option)
endfunction

function! sourcetrail#error(message)
    echohl Error | echomsg a:message | echohl None
endfunction

" Configuration
let g:sourcetrail_to_vim_port =
      \ get( g:, 'sourcetrail_to_vim_port', 6666 )

let g:vim_to_sourcetrail_port =
      \ get( g:, 'vim_to_sourcetrail_port', 6667 )

let g:sourcetrail_ip =
      \ get( g:, 'sourcetrail_ip', "localhost" )

let g:sourcetrail_autostart = 
      \ get( g:, 'sourcetrail_autostart', 0 )

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')


" Load Python script
if filereadable($VIMRUNTIME."/plugin/python/sourcetrail.py")
  pyfile $VIMRUNTIME/plugin/sourcetrail.py
elseif filereadable($HOME."/.vim/plugin/python/sourcetrail.py")
  pyfile $HOME/.vim/plugin/python/sourcetrail.py
else
  " when we use pathogen for instance
  let $CUR_DIRECTORY=escape(expand('<sfile>:p:h'), '\')

  if filereadable($CUR_DIRECTORY."/sourcetrail.py")
    pyfile $CUR_DIRECTORY/sourcetrail.py
  else
    call confirm('vdebug.vim: Unable to find sourcetrail.py. Place it in either your home vim directory or in the Vim runtime directory.', 'OK')
  endif
endif


function! sourcetrail#ShowSettings()
python << endPython
Sourcetrail.print_settings()
endPython
endfunction

function! sourcetrail#SourcetrailInit()
python << endPython
Sourcetrail.start_server()
endPython
endfunction

function! sourcetrail#SourcetrailShutdown()
python << endPython
Sourcetrail.stop_server()
endPython
endfunction

function! sourcetrail#ActivateToken()
python << endPython
Sourcetrail.send_activate_token()
endPython
endfunction

function! sourcetrail#RestartServer()
python << endPython
Sourcetrail.restart_server()
endPython
endfunction

function! sourcetrail#UpdateBuffer()
python << endPython
Sourcetrail.update_buffer()
endPython
endfunction

if has('python')
	augroup SourcetrailPlugin
		autocmd FocusGained,BufEnter	* :call sourcetrail#UpdateBuffer()
		autocmd VimLeavePre				* :call sourcetrail#SourcetrailShutdown()
	augroup END
endif

python sourcetrail = Sourcetrail()

if( sourcetrail#get("sourcetrail_autostart") )
	call sourcetrail#SourcetrailInit()
endif

