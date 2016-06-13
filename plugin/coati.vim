" Exit when already loaded (or "compatible" mode set)
if exists("g:coati_loaded") || &cp
    finish
endif

" Vars used by this script, don't change
let g:coati_loaded = 1

if !has('python')
	call coati#error("Error: Required vim compiled with +python")
	finish
endif

command! CoatiSettings call coati#ShowSettings()
command! CoatiActivateToken call coati#ActivateToken()
command! CoatiStartServer call coati#CoatiInit()
command! CoatiRestartServer call coati#RestartServer()
command! CoatiStopServer call coati#CoatiShutdown()
command! CoatiRefresh call coati#UpdateBuffer()

