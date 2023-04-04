#!/usr/bin/env bash

VENV=$1

SESSION="farmer_app"

SESSIONEXISTS=$(tmux list-sessions | grep $SESSION)

function active_env() {
    tmux send-keys -t $SESSION:$WINDOW "source $VENV/bin/activate" C-m
}

if [ -z "$SESSIONEXISTS" ];
then
    tmux new-session -d -s $SESSION

    WINDOW=0
    tmux rename-window -t "$SESSION:$WINDOW" 'docker'
    tmux send-keys -t $SESSION:$WINDOW 'docker compose up' C-m

    WINDOW=1
    tmux new-window -t $SESSION:$WINDOW -n 'lvim'
    tmux send-keys -t $SESSION:$WINDOW 'lvim .' C-m

    WINDOW=2
    tmux new-window -t $SESSION:$WINDOW -n 'users'
    active_env
    tmux send-keys -t $SESSION:$WINDOW 'python ./src/beans_silo.py' C-l C-m

    tmux split-window -h -p 50
    tmux send-keys -t $SESSION:$WINDOW 'sleep 6' C-l C-m
    active_env
    tmux send-keys -t $SESSION:$WINDOW 'python ./src/grain_stock_mgmt.py' C-l C-m

    tmux split-window -v -p 67
    tmux send-keys -t $SESSION:$WINDOW 'sleep 6' C-m
    active_env
    tmux send-keys -t $SESSION:$WINDOW 'python ./src/fleet_management.py' C-l C-m

    tmux split-window -v -p 50
    tmux send-keys -t $SESSION:$WINDOW 'sleep 6' C-m
    active_env
    tmux send-keys -t $SESSION:$WINDOW 'python ./src/farmer_app.py' C-l C-m

    tmux select-pane -t 0
    tmux split-window -v -p 50
    active_env
    tmux send-keys -t $SESSION:$WINDOW 'python ./src/truck_yard_gate.py' C-l C-m
fi

tmux attach-session -t $SESSION:2
