#!/usr/bin/env bash

## Screenshot Applet con Flameshot

# Importa tema
source "$HOME"/.config/rofi/applets/shared/theme.bash
theme="$type/$style"

# Elementi tema
prompt='Screenshot'
dir="$(xdg-user-dir PICTURES)/Screenshots"
mesg="DIR: $dir"

mkdir -p "$dir"

if [[ "$theme" == *'type-1'* ]]; then
    list_col='1'
    list_row='5'
    win_width='400px'
elif [[ "$theme" == *'type-3'* ]]; then
    list_col='1'
    list_row='5'
    win_width='120px'
elif [[ "$theme" == *'type-5'* ]]; then
    list_col='1'
    list_row='5'
    win_width='520px'
elif [[ ( "$theme" == *'type-2'* ) || ( "$theme" == *'type-4'* ) ]]; then
    list_col='5'
    list_row='1'
    win_width='670px'
fi

# Opzioni
layout=$(grep 'USE_ICON' "$theme" | cut -d'=' -f2)
if [[ "$layout" == 'NO' ]]; then
    option_1=" Capture Desktop"
    option_2=" Capture Area"
    option_3=" Capture Window"
    option_4=" Capture in 5s"
    option_5=" Capture in 10s"
else
    option_1=""
    option_2=""
    option_3=""
    option_4=""
    option_5=""
fi

# Rofi CMD
rofi_cmd() {
    rofi -theme-str "window {width: $win_width;}" \
        -theme-str "listview {columns: $list_col; lines: $list_row;}" \
        -theme-str 'textbox-prompt-colon {str: "";}' \
        -dmenu \
        -p "$prompt" \
        -mesg "$mesg" \
        -markup-rows \
        -theme ${theme}
}

# Passa a rofi
run_rofi() {
    echo -e "$option_1\n$option_2\n$option_3\n$option_4\n$option_5" | rofi_cmd
}

# Comandi flameshot
shotnow() {
    flameshot full --clipboard --path "$dir"

}

shotarea() {
    flameshot gui --clipboard --path "$dir"

}

shotwin() {
    flameshot gui --clipboard --path "$dir"

}

shot5() {
    flameshot full --delay 5000 --clipboard --path "$dir"

}

shot10() {
    flameshot full --delay 10000 --clipboard --path "$dir"

}

# Esegui
run_cmd() {
    case "$1" in
        --opt1) shotnow ;;
        --opt2) shotarea ;;
        --opt3) shotwin ;;
        --opt4) shot5 ;;
        --opt5) shot10 ;;
    esac
}

# Azioni
chosen="$(run_rofi)"
case ${chosen} in
    $option_1) run_cmd --opt1 ;;
    $option_2) run_cmd --opt2 ;;
    $option_3) run_cmd --opt3 ;;
    $option_4) run_cmd --opt4 ;;
    $option_5) run_cmd --opt5 ;;
esac
