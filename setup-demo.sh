#! /bin/bash 
session_file=$1
demo_name=${2:-Demo}
session_name=${3:-demosession}

echo Demo $demo_name with file $session_file
echo - Kill existing sessions $session_name
tmux kill-session -t $session_name 2> /dev/null
echo - New detached session $session_name
tmux new-session -s $session_name -n $demo_name -d 

echo - Start presentation terminal

bash -c '/Volumes/Macintosh\ HD/Applications/Alacritty.app/Contents/MacOS/alacritty --config-file ./presentation.yml -e tmux attach-session -d $session_name'&
vim $session_file

