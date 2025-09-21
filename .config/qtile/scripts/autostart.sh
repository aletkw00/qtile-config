#!/bin/sh

# lxsession &
lxsession -s qtile -e qtile &
dunst &
nm-applet &
#pasystray &
#eval "$(dbus-launch --sh-syntax --exit-with-session)"
~/.config/qtile/scripts/set-random-wallpaper.sh init
#/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
