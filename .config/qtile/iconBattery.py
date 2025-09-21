import psutil
from qtile_extras import widget

battery_icons = ["󰁺", "󰁻", "󰁼", "󰁽", "󰁾", "󰁿", "󰂀", "󰂁", "󰂂", "󱟢", "󰂄", "󱟨"]


class IconBattery(widget.Battery):
    def __init__(self, **config):
        super().__init__(**config)

    def build_string(self, status):
        """
        Override Battery.build_string() so we can choose our own icons.
        `status` is a namedtuple with:
            percent, power, secsleft, wattage, char
        """
        try:
            battery = psutil.sensors_battery()
            percent = int(status.percent * 100)
            if battery.power_plugged:
                icon = battery_icons[-2]  # charging
            else:
                index = min(percent // 10, 9)
                icon = battery_icons[index]

            # return f"{icon} {percent}%"
            return f"{icon} {percent}% "
        except Exception as e:
            return f"{battery_icons[-1]} {e}  "
