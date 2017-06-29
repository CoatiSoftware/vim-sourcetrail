" Exit when already loaded (or "compatible" mode set)
if exists("g:sourcetrail_loaded") || &cp
    finish
endif

" Vars used by this script, don't change
let g:sourcetrail_loaded = 1

if !has('python') && !has('python3')
	call sourcetrail#error("Error: Required vim compiled with +python")
	finish
endif

command! SourcetrailSettings call sourcetrail#ShowSettings()
command! SourcetrailActivateToken call sourcetrail#ActivateToken()
command! SourcetrailStartServer call sourcetrail#SourcetrailInit()
command! SourcetrailRestartServer call sourcetrail#RestartServer()
command! SourcetrailStopServer call sourcetrail#SourcetrailShutdown()
command! SourcetrailRefresh call sourcetrail#UpdateBuffer()

