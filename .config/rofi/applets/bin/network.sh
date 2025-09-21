#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Modified for rofi theme integration

## Style
source "$HOME/.config/rofi/applets/shared/theme.bash"
theme="$type/$style"
theme_list="$type_list/$style"
theme_custom="$type_custom/$style"
rofi_cmd="rofi -theme $theme -dmenu -i"
rofi_cmd_list="rofi -theme $theme_list -dmenu -i"
rofi_cmd_custom="rofi -theme $theme_custom -dmenu -i"


## Colors & Icons
ENABLED_COLOR="#A3BE8C"
DISABLED_COLOR="#D35F5E"
SIGNAL_ICONS=("󰤟 " "󰤢 " "󰤥 " "󰤨 ")
SECURED_SIGNAL_ICONS=("󰤡 " "󰤤 " "󰤧 " "󰤪 ")
WIFI_CONNECTED_ICON=" "
ETHERNET_CONNECTED_ICON=" "

SESSION_TYPE="x11"   # force X11

get_status() {
    if nmcli -t -f TYPE,STATE device status | grep 'ethernet:connected' > /dev/null; then
        status_icon="󰈀"
        status_color=$ENABLED_COLOR
    elif nmcli -t -f TYPE,STATE device status | grep 'wifi:connected' > /dev/null; then
        wifi_info=$(nmcli --terse --fields "IN-USE,SIGNAL,SECURITY,SSID" device wifi list --rescan no | grep '\*')
        if [ -n "$wifi_info" ]; then
            IFS=: read -r in_use signal security ssid <<< "$wifi_info"
            signal_level=$((signal / 25))
            signal_icon="${SIGNAL_ICONS[$signal_level]}"
            if [[ "$security" =~ WPA || "$security" =~ WEP ]]; then
                signal_icon="${SECURED_SIGNAL_ICONS[$signal_level]}"
            fi
            status_icon="$signal_icon"
            status_color=$ENABLED_COLOR
        else
            status_icon=" "
            status_color=$DISABLED_COLOR
        fi
    else
        status_icon=" "
        status_color=$DISABLED_COLOR
    fi

    # Polybar-style format for X11
    echo "%{F$status_color}$status_icon%{F-}"
}

manage_wifi() {
    nmcli --terse --fields "IN-USE,SIGNAL,SECURITY,SSID" device wifi list > /tmp/wifi_list.txt

    ssids=()
    formatted_ssids=()
    active_ssid=""

    while IFS=: read -r in_use signal security ssid; do
        [[ -z "$ssid" ]] && continue

        signal_level=$((signal / 25))
        signal_icon="${SIGNAL_ICONS[$signal_level]}"
        if [[ "$security" =~ WPA || "$security" =~ WEP ]]; then
            signal_icon="${SECURED_SIGNAL_ICONS[$signal_level]}"
        fi

        formatted="$signal_icon $ssid"
        if [[ "$in_use" =~ \* ]]; then
            active_ssid="$ssid"
            formatted="$WIFI_CONNECTED_ICON $formatted"
        fi
        ssids+=("$ssid")
        formatted_ssids+=("$formatted")
    done < /tmp/wifi_list.txt

    formatted_list=$(printf "%s\n" "${formatted_ssids[@]}")

    chosen_network=$(echo -e "$formatted_list" | $rofi_cmd_list -selected-row 1 -p "Wi-Fi SSID: ")
    [[ -z "$chosen_network" ]] && { rm /tmp/wifi_list.txt; return; }

    ssid_index=-1
    for i in "${!formatted_ssids[@]}"; do
        [[ "${formatted_ssids[$i]}" == "$chosen_network" ]] && ssid_index=$i && break
    done
    chosen_id="${ssids[$ssid_index]}"

    if [[ "$chosen_id" == "$active_ssid" ]]; then
        action=$(echo -e "󰸋  Connect\n  Disconnect\n  Forget" | $rofi_cmd_list -p "Action:" -lines 3)
    else
        action=$(echo -e "󰸋  Connect\n  Forget" | $rofi_cmd_list -p "Action:" -lines 2)
    fi

    case $action in
        "󰸋  Connect")
            saved_connections=$(nmcli -g NAME connection show)
            if echo "$saved_connections" | grep -Fx "$chosen_id" > /dev/null; then
                nmcli connection up id "$chosen_id" && notify-send "Connected" "You are now connected to $chosen_id"
            else
                wifi_password=$($rofi_cmd_custom -password -p "Password for $chosen_id:")
                nmcli device wifi connect "$chosen_id" password "$wifi_password" && notify-send "Connected" "You are now connected to $chosen_id"
            fi
            ;;
        "  Disconnect")
            nmcli device disconnect wlan0 && notify-send "Disconnected" "You have been disconnected from $chosen_id."
            ;;
        "  Forget")
            nmcli connection delete id "$chosen_id" && notify-send "Forgotten" "The network $chosen_id has been forgotten."
            ;;
    esac

    rm /tmp/wifi_list.txt
}

manage_ethernet() {
    eth_devices=$(nmcli device status | awk '/ethernet/ {print $1}')
    [[ -z "$eth_devices" ]] && { notify-send "Error" "Ethernet device not found."; return; }

    eth_list=""
    for dev in $eth_devices; do
        dev_status=$(nmcli device status | awk -v d=$dev '$1==d {print $3}')
        [[ "$dev_status" == "connected" ]] && eth_list+="$ETHERNET_CONNECTED_ICON$dev\n" || eth_list+="$dev\n"
    done

    chosen_device=$(echo -e "$eth_list" | $rofi_cmd_list -p "Select Ethernet device: ")
    [[ -z "$chosen_device" ]] && return

    chosen_device=${chosen_device//$ETHERNET_CONNECTED_ICON/}
    dev_status=$(nmcli device status | awk -v d=$chosen_device '$1==d {print $3}')

    case $dev_status in
        connected) nmcli device disconnect "$chosen_device" && notify-send "Disconnected" "You have been disconnected from $chosen_device." ;;
        disconnected) nmcli device connect "$chosen_device" && notify-send "Connected" "You are now connected to $chosen_device." ;;
        *) notify-send "Error" "Unable to determine the action for $chosen_device." ;;
    esac
}

main_menu() {
    # Ensure NetworkManager is running
    if ! pgrep -x "NetworkManager" > /dev/null; then
        notify-send "Starting NetworkManager..."
        sudo systemctl start NetworkManager
    fi

    wifi_status=$(nmcli -fields WIFI g)
    if [[ "$wifi_status" =~ "enabled" ]]; then
        wifi_toggle="󰤨 "
        wifi_toggle_command="off"
        manage_wifi_btn="\n󱓥 Manage Wi-Fi"
    else
        wifi_toggle="󰤤 "
        wifi_toggle_command="on"
        manage_wifi_btn=""
    fi

    chosen_option=$(echo -e "$wifi_toggle$manage_wifi_btn\n󱓥 Manage Ethernet" | $rofi_cmd -p " Network Management: ")
    case $chosen_option in
        "$wifi_toggle") nmcli radio wifi $wifi_toggle_command ;;
        "󱓥 Manage Wi-Fi") manage_wifi ;;
        "󱓥 Manage Connection") nm-connection-editor
    esac
}

main_menu "$@"
