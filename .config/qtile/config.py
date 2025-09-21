from libqtile import bar, layout, qtile, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from iconBattery import IconBattery
import files
import json
import psutil
import os
import subprocess
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration
from qtile_extras.widget.decorations import PowerLineDecoration

# Reuse your fontsize variable
mod = "mod4"
terminal = "alacritty"
colorsJson = os.path.expanduser('~/.cache/wal/colors.json')
colordict = json.load(open(colorsJson))['colors']
colors = [colordict[f'color{i}'] for i in range(16)]

decor_rounded = {
    "decorations": [
        RectDecoration(colour=colors[2], radius=13, filled=True, padding_y=0)
    ]
}

decor_rounded_group = {
    "decorations": [
        RectDecoration(colour=colors[2], radius=13, filled=True, padding_y=0, group=True)
    ]
}

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "l",
        lazy.layout.grow_right().when(layout="columns"),
        lazy.layout.grow().when(layout=["monadtall", "monadwide"]),
        desc="Grow window to the right or grow master in MonadTall"
    ),
    Key([mod, "control"], "k",
        lazy.layout.grow_up().when(layout="columns"),
        lazy.layout.shrink().when(layout="monadtall"),
        desc="Grow window up or shrink master in MonadTall"
    ),
    Key([mod], "n",
        lazy.layout.normalize(),
        desc="Reset all window sizes"
    ),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    # Volume control
    Key([], "XF86AudioRaiseVolume", lazy.spawn(files.resolve_file_path("${scripts}/notify-volume.sh up")), desc="Increase volume"),
    Key([], "XF86AudioLowerVolume", lazy.spawn(files.resolve_file_path("${scripts}/notify-volume.sh down")), desc="Decrease volume"),
    Key([], "XF86AudioMute", lazy.spawn(files.resolve_file_path("${scripts}/notify-volume.sh mute")), desc="Mute audio"),

    # Brightness control (requires brightnessctl or xbacklight)
    Key([], "XF86MonBrightnessUp", lazy.spawn(files.resolve_file_path("${scripts}/notify-brightnessctl.sh up")), desc="Increase brightness"),
    Key([], "XF86MonBrightnessDown", lazy.spawn(files.resolve_file_path("${scripts}/notify-brightnessctl.sh down")), desc="Decrease brightness"),
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "shift"], "f", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen"),
    Key([mod], "t", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload Qtile config"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command prompt"),
    Key([mod], "e", lazy.spawn("subl"), desc="Open Sublime-text instance"),
    Key([mod], "b", lazy.spawn("firefox"), desc="Opens FIrefox"),
    Key([mod], "f", lazy.spawn("thunar"), desc="Open FileManger"),
    Key([mod], "d", lazy.spawn(files.resolve_file_path("${rofi_home}/launchers/type-6/launcher.sh")), desc="Run launcher"),
    Key([mod],"p", lazy.spawn(files.resolve_file_path("${scripts}/set-random-wallpaper.sh")), desc="Set random wallpaper"),
    Key([mod, "shift"],"m", lazy.spawn("betterlockscreen -l"), desc="Lock screen"),
    Key([], "Print",
        lazy.spawn(files.resolve_file_path("${scripts}/screenshot.sh full")),
        desc="Take a screenshot (full)"),

    # Fullscreen screenshot
    Key([mod], "Print",
        lazy.spawn(files.resolve_file_path("${scripts}/screenshot.sh gui")),
        desc="Take a screenshot (selection)"),
]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )

groups = [Group(i) for i in "123456789"]

for i in groups:
    keys.extend(
        [
            # mod + group number = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc=f"Switch to group {i.name}",
            ),
            # mod + shift + group number = switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc=f"Switch to & move focused window to group {i.name}",
            ),
            # Or, use below if you prefer not to switch to that group.
            # # mod + shift + group number = move focused window to group
            # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
            #     desc="move focused window to group {}".format(i.name)),
        ]
    )

def init_layout_theme():
    return {
        "margin": 15,
        "border_width": 2,
        "border_focus": colors[8],
        "border_normal": colors[0],
    }


layout_theme = init_layout_theme()

layouts = [
    layout.MonadTall(**layout_theme, single_stack=False),
    layout.MonadWide(**layout_theme),
    layout.Matrix(**layout_theme)
]


fontsize = 14

widget_defaults = dict(
    font="Noto Sans Bold",
    fontsize=13,
    padding=0,
)
extension_defaults = widget_defaults.copy()

def init_widgets_list():
    widgets_list = [
        widget.GroupBox(
            fontsize = fontsize,
            margin_y = 5,
            margin_x = 12,
            padding_y = 0,
            padding_x = 2,
            borderwidth = 3,
            active = colors[8],
            inactive = colors[9],
            rounded = False,
            highlight_color = colors[0],
            highlight_method = "line",
            this_current_screen_border = colors[7],
            this_screen_border = colors [4],
            other_current_screen_border = colors[7],
            other_screen_border = colors[4],
        ),
        widget.TextBox(
            text = '|',
            foreground = colors[9],
            padding = 2,
            fontsize = fontsize
        ),
        widget.LaunchBar(
            progs = [
                ("󰈹", "firefox", "Firefox web browser"),
                ("", "thunar", "Thunar file manager"),
            ], 
            fontsize = fontsize,
            padding = 10,
            foreground = colors[3],
        ),
        widget.TextBox(
            text = '|',
            foreground = colors[9],
            padding = 2,
            fontsize = fontsize
        ),
        widget.WindowName(
            foreground = colors[6],
            padding = 8,
            fontsize = fontsize,
            max_chars = 40
        ),
        widget.Spacer(
            bar.STRETCH
        ),
        widget.Clock(
            **decor_rounded,
            font="Noto Sans Bold",
            foreground=colors[15],
            fontsize=fontsize,
            mouse_callbacks={'Button1': lambda: qtile.cmd_spawn('gsimplecal')},
            format="  %b %d  %H:%M  ",
        ),
        widget.Spacer(
            bar.STRETCH
        ),
        widget.CPU(
            foreground = colors[4],
            padding = 8, 
            fontsize = fontsize,
            mouse_callbacks = {'Button1': lambda: qtile.cmd_spawn(f"{terminal} -e bash -ic htop")},
            format = '  Cpu: {load_percent}%',
        ),
        widget.Memory(
            foreground = colors[8],
            padding = 8, 
            fontsize = fontsize, 
            mouse_callbacks = {'Button1': lambda: qtile.cmd_spawn(f"{terminal} -e bash -ic htop")},
            format = '{MemUsed: .0f}{mm}',
            fmt = '󰍛  Mem: {}',
        ),
        widget.DF(
            update_interval = 60,
            foreground = colors[5],
            padding = 8,
            fontsize = fontsize, 
            mouse_callbacks = {'Button1': lambda: qtile.cmd_spawn('notify-disk')},
            partition = '/home',
            format = '{uf}{m} free',
            fmt = '󰨣  Disk: {}',
            visible_on_warn = False,
        ),
        widget.Systray(
            # **decor_rounded_group,
            # background=colors[2],
            icon_size=20,
            padding=4
        ),
        widget.Spacer(
            background=colors[0],
            length=15,
        ), 
        widget.LaunchBar(
            progs = [
                ("", "pavucontrol -t 3", "Output Devices"),
                ("", "pavucontrol -t 4", "Input Devices"),
            ], 
            fontsize = fontsize,
            padding = 8,
            foreground = colors[15],
            **decor_rounded_group
        ),
        IconBattery(
            **decor_rounded_group,
            update_interval=10,
            notify_below=20,
            low_foreground=colors[2],
            foreground=colors[15],
            fontsize=fontsize,
            padding=5,
        ),
        widget.Spacer(
            length=15,
        ),
        widget.Image(
            filename=files.resolve_file_path("${qtile_home}/icons/powermenu.png"),
            padding=0,
            fontsize=10,
            mouse_callbacks={
                "Button1": lambda: qtile.cmd_spawn(files.resolve_file_path("${rofi_home}/applets/bin/powermenu.sh"))
            },
            **decor_rounded,
        ),
        widget.Spacer(
            length=8,
        ),
        
    ]
    return widgets_list


def init_screens():
    try:
        xrandr_output = subprocess.check_output("xrandr --query", shell=True).decode()
        num_monitors = xrandr_output.count(" connected")
    except Exception:
        num_monitors = 1  # fallback se xrandr non funziona

    screens = []
    for i in range(num_monitors):
        if i == num_monitors - 1:
            screens.append(
                Screen(
                    top=bar.Bar(
                        widgets=init_widgets_list(),
                        size=25,
                        background=colors[0],
                        opacity=1,
                        margin=[8, 12, 0, 12],
                        border_width=[4, 4, 4, 4],
                        border_color=colors[0],
                    )
                )
            )
        else:
            # Tutti gli altri monitor senza barra
            screens.append(Screen())

    return screens

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    border_focus=colors[8],
    border_width=2,
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),   # gitk
        Match(wm_class="dialog"),         # dialog boxes
        Match(wm_class="download"),       # downloads
        Match(wm_class="error"),          # error msgs
        Match(wm_class="file_progress"),  # file progress boxes
        Match(wm_class='kdenlive'),       # kdenlive
        Match(wm_class="makebranch"),     # gitk
        Match(wm_class="maketag"),        # gitk
        Match(wm_class="notification"),   # notifications
        Match(wm_class='pinentry-gtk-2'), # GPG key password entry
        Match(wm_class="ssh-askpass"),    # ssh-askpass
        Match(wm_class="toolbar"),        # toolbars
        Match(wm_class="pavucontrol"),    # pavucontrol
        Match(title="branchdialog"),      # gitk
        Match(title='Confirmation'),      # tastyworks exit box
        Match(title='Qalculate!'),        # qalculate-gtk
        Match(title="pinentry"),          # GPG key password entry
        Match(title="tastycharts"),       # tastytrade pop-out charts
        Match(title="tastytrade"),        # tastytrade pop-out side gutter
        Match(title="tastytrade - Portfolio Report"), # tastytrade pop-out allocation
        Match(wm_class="tasty.javafx.launcher.LauncherFxApp"), # tastytrade settings
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None



# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

if __name__ in ["config", "__main__"]:
    screens = init_screens()


@hook.subscribe.screen_change
def restart_on_randr(event):
    subprocess.call(["xrandr", "--auto"])
    event.qtile.restart()

@hook.subscribe.startup_once
def autostart():
    with open("/home/alessio/autostart.log", "w") as f:
        f.write("Starting autostart.sh and picom...\n")
        try:
            home = os.path.expanduser(files.resolve_file_path("${scripts}/autostart.sh"))
            subprocess.Popen([home], stdout=f, stderr=f)
            subprocess.Popen(["picom", "--config", files.resolve_file_path("${picom}/picom.conf")], stdout=f, stderr=f)
        except Exception as e:
            f.write(f"Error: {e}\n")

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"