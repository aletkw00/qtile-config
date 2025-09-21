#!/bin/bash

BRIGHTCTL="/usr/bin/brightnessctl"
DUNSTIFY="/usr/bin/dunstify"

# Modifica luminosità
case "$1" in
    up)
        $BRIGHTCTL set +5%
        ;;
    down)
        $BRIGHTCTL set 5%-
        ;;
esac

# Recupera percentuale
BRIGHTNESS=$($BRIGHTCTL get)
MAX=$($BRIGHTCTL max)
PERC=$((BRIGHTNESS * 100 / MAX))

# Scegli icona
if   [ "$PERC" -le 30 ]; then ICON="󱩎"
elif [ "$PERC" -le 70 ]; then ICON="󱩏"
else ICON="󱩐"
fi

# Notifica
$DUNSTIFY -a "Luminosità" -r 9994 -u normal "$ICON  Brightness: $PERC%" -h int:value:"$PERC"
