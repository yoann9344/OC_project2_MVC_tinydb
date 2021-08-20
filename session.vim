let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/controllers
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +0 layout_controllers/plugins/selectable.py
badd +7 layout_controllers/plugins/editable.py
badd +37 ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/models/mymodels/tournament.py
badd +154 layout_controllers/tournament_creator.py
badd +0 ~/cours/OC/occhess\ -\ p3/repo/README.md
badd +40 ~/cours/OC/occhess\ -\ p3/repo/.gitignore
badd +0 pages/welcome.py
badd +0 ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/models/mymodels/player.py
badd +93 page.py
badd +1 ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/db.json
badd +34 ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/main.py
badd +24 ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/models/model.py
badd +105 loop.py
badd +1 pages/select_tournament_players.py
badd +1 pages/table.py
badd +24 layout_controllers/table.py
badd +10 layout_controller.py
badd +1 layout_controllers/__init__.py
badd +16 ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/views/view.py
badd +301 ~/cours/OC/occhess\ -\ p3/repo/.venv/lib/python3.9/site-packages/rich/layout.py
badd +0 ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/views/table.py
argglobal
%argdel
set stal=2
tabnew
tabnew
tabnew
tabnew
tabnew
tabnew
tabnew
tabnew
tabnew
tabnew
tabnew
tabnew
tabnew
tabrewind
edit layout_controllers/plugins/selectable.py
argglobal
balt layout_controllers/plugins/selectable.py
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 51 - ((43 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 51
normal! 039|
tabnext
edit layout_controllers/plugins/editable.py
argglobal
balt layout_controllers/plugins/editable.py
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 20 - ((19 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 20
normal! 056|
tabnext
edit layout_controllers/tournament_creator.py
argglobal
balt layout_controllers/plugins/editable.py
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 5 - ((4 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 5
normal! 023|
tabnext
edit pages/select_tournament_players.py
argglobal
balt layout_controllers/table.py
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 9 - ((8 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 9
normal! 029|
tabnext
edit layout_controllers/table.py
argglobal
balt ~/cours/OC/occhess\ -\ p3/repo/.gitignore
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 193 - ((52 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 193
normal! 012|
lcd ~/cours/OC/occhess\ -\ p3/repo
tabnext
edit ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/views/table.py
argglobal
balt ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/views/table.py
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 67 - ((27 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 67
normal! 0
lcd ~/cours/OC/occhess\ -\ p3/repo
tabnext
edit ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/controllers/layout_controller.py
argglobal
balt ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/controllers/layout_controllers/__init__.py
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 43 - ((42 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 43
normal! 054|
lcd ~/cours/OC/occhess\ -\ p3/repo
if exists(':tcd') == 2 | tcd ~/cours/OC/occhess\ -\ p3/repo | endif
tabnext
edit ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/controllers/loop.py
argglobal
balt ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/controllers/layout_controllers/tournament_creator.py
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 170 - ((42 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 170
normal! 048|
tabnext
edit ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/controllers/pages/welcome.py
argglobal
balt ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/controllers/loop.py
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 14 - ((13 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 14
normal! 017|
tabnext
edit ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/models/model.py
argglobal
balt ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/controllers/layout_controllers/tournament_creator.py
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 23 - ((21 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 23
normal! 014|
tabnext
edit ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/models/mymodels/tournament.py
argglobal
balt ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/controllers/layout_controllers/tournament_creator.py
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 48 - ((42 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 48
normal! 0
tabnext
edit ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/models/mymodels/player.py
argglobal
balt ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/models/mymodels/tournament.py
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 12 - ((11 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 12
normal! 050|
tabnext
edit ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/main.py
argglobal
balt ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/db.json
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 9 - ((8 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 9
normal! 014|
tabnext
edit ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/db.json
argglobal
balt ~/cours/OC/occhess\ -\ p3/repo/chess_tournament/main.py
setlocal fdm=indent
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=4
setlocal fml=1
setlocal fdn=10
setlocal nofen
let s:l = 1 - ((0 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 0
tabnext 5
set stal=1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0&& getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxtToOFc
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
set hlsearch
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
