#! /bin/bash 
session_file=$1
demo_name=${2:-Demo}
session_name=${3:-demosession}
base_path=${4:-`pwd`}

echo Demo $demo_name with file $session_file
echo - Kill existing sessions $session_name
tmux kill-session -t $session_name 2> /dev/null
echo - New detached session $session_name
tmux new-session -s $session_name -n $demo_name -d -c $base_path bash

echo - Start presentation terminal
#bash -c 'open -a Alacritty.app --args -vvv --config-file $base_path/presentation.yml -e tmux attach-session -d $session_name'&
bash -c '/Volumes/Macintosh\ HD/Applications/Alacritty.app/Contents/MacOS/alacritty --config-file ./presentation.yml -e tmux attach-session -d $session_name'&
vim $session_file -c 'map <PageDown> :.w !grep ^tmux \| bash<CR><CR>/^tmux<CR>mp'
