#!/bin/bash

DIR="$HOME/Pictures/Screenshots"
mkdir -p "$DIR"

notify_view() {
    last_file=$(ls -t "$DIR"/*.png 2>/dev/null | head -n 1)
    if [[ -f "$last_file" ]]; then
        dunstify -i "$last_file" -u low --replace=699 "Screenshot Saved → $last_file"
    else
        dunstify -u low --replace=699 "Screenshot failed"
    fi
}

# Flameshot command passed as argument
if [ "$1" = "gui" ]; then
    flameshot gui --clipboard --path "$DIR"
    if [[ $? -eq 0 ]]; then
        notify_view
    fi
elif [ "$1" = "full" ]; then
    flameshot full --clipboard --path "$DIR"
    if [[ $? -eq 0 ]]; then
        notify_view
    fi
fi

