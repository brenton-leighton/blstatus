from typing import Callable
from pydbus.bus import Bus

from . import config

UPOWER_TYPE_BATTERY = 2
UPOWER_STATE_CHARGING = 1
UPOWER_STATE_DISCHARGING = 2
UPOWER_STATE_FULLY_CHARGED = 4


def get_state_abbreviation(value):
    """Return a single character abbreviation for the battery state"""
    if value == UPOWER_STATE_CHARGING:
        return '+'
    elif value == UPOWER_STATE_DISCHARGING:
        return '-'
    elif value == UPOWER_STATE_FULLY_CHARGED:
        return ''
    else:
        return '?'


def format_time(total_seconds):
    if total_seconds == 0:
        return ''

    total_minutes = total_seconds // 60

    hours = total_minutes // 60
    minutes = total_minutes % 60

    return ' ({}:{:0>2})'.format(hours, minutes)


class Battery:
    _publish_status = None
    _signal_text = ''
    _spacer = ''
    _system_bus = None
    _device_proxy = None
    text = ''

    def __init__(self, system_bus: Bus, publish_status: Callable[[], None], spacer=''):

        self._publish_status = publish_status  # Function to update the full status text
        self._signal_text = config.battery_signal_text if config.enable_signal_text else ''  # statuscmd signal text
        self._spacer = spacer  # Spacer text added after status
        self._system_bus = system_bus

        upower_proxy = self._system_bus.get('org.freedesktop.UPower')
        devices = upower_proxy.EnumerateDevices()

        # For each UPower device
        for device in devices:
            device_proxy = self._system_bus.get('org.freedesktop.UPower', device)

            # Find the first battery
            if device_proxy.Type == UPOWER_TYPE_BATTERY:
                self._device_proxy = device_proxy
                break

        if self._device_proxy is not None:
            self._device_proxy.PropertiesChanged.connect(self._update_and_publish)
            self.update_text()  # Initial update of battery status

    def update_text(self):
        """Update battery status text"""

        # Get battery state
        state = self._device_proxy.State

        # Get the time string
        time = ''

        if state == UPOWER_STATE_CHARGING:
            time = format_time(self._device_proxy.TimeToFull)
        elif state == UPOWER_STATE_DISCHARGING:
            time = format_time(self._device_proxy.TimeToEmpty)

        if time == '':
            state = UPOWER_STATE_FULLY_CHARGED

        # Get battery charge percent
        battery_percent = round(self._device_proxy.Percentage)

        # Format status text
        self.text = f'{self._signal_text}{get_state_abbreviation(state)}{str(battery_percent)}%{time}{self._spacer}'

    def _update_and_publish(self, *params):
        """Callback for the PropertiesChanged signal of the battery device proxy"""
        self.update_text()  # Update battery status text
        self._publish_status()  # Publish full status text
