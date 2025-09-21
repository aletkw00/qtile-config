#!/bin/bash

# Configura percorso completo ai comandi per sicurezza
PAMIXER="/usr/bin/pamixer"
DUNSTIFY="/usr/bin/dunstify"

# Modifica volume (+ o -)
case "$1" in
    up)
        $PAMIXER -i 5
        ;;
    down)
        $PAMIXER -d 5
        ;;
    mute)
        $PAMIXER -t
        ;;
esac

# Recupera stato volume
VOLUME=$($PAMIXER --get-volume)
MUTE=$($PAMIXER --get-mute)

# Imposta icona
if [ "$MUTE" = "true" ]; then
    ICON="󰖁"
else
    if   [ "$VOLUME" -le 30 ]; then ICON=""
    elif [ "$VOLUME" -le 70 ]; then ICON=""
    else ICON=""
    fi
fi

# Notifica con barra
$DUNSTIFY -a "Volume" -r 9993 -u normal "$ICON   Volume: $VOLUME%" -h int:value:"$VOLUME"
