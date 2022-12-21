from typing import Callable
from pydbus.bus import Bus

import config
import inhibit

NM_DEVICE_TYPE_ETHERNET = 1
NM_DEVICE_TYPE_WIFI = 2

NM_DEVICE_STATE_ACTIVATED = 100

active_connection_types = ['802-3-ethernet', '802-11-wireless']


def format_bps(value):
    if value >= 1000:
        return ''.join([str(int(value / 1000)) + ' Gbit/s'])
    else:
        return ''.join([str(value) + ' Mbit/s'])


def format_ssid(value_list):
    char_list = []
    for v in value_list:
        char_list.append(chr(v))

    return ''.join(char_list)


class Network:
    _publish_status = None
    _wifi_signal_text = ''
    _ethernet_signal_text = ''
    _spacer = ''
    text = ''
    _system_bus = None
    _nm_proxy = None
    _active_connection_proxies = []
    _active_connection_property_subs = []
    _device_proxies = []

    def __init__(self,
                 system_bus: Bus,
                 publish_status: Callable[[], None],
                 wifi_signal_text='',
                 ethernet_signal_text='',
                 spacer=''):

        self._publish_status = publish_status
        self._wifi_signal_text = wifi_signal_text if config.enable_signal_text else ''  # statuscmd signal text
        self._ethernet_signal_text = ethernet_signal_text if config.enable_signal_text else ''
        self._spacer = spacer
        self._system_bus = system_bus

        self._nm_proxy = self._system_bus.get('org.freedesktop.NetworkManager')

        self.update_proxies_and_text()
        self._nm_proxy.PropertiesChanged.connect(self._callback_nm)

    def update_proxies_and_text(self):
        """ Update active connection proxies, device proxies, and status text"""

        self._device_proxies.clear()

        # Update active connection proxies
        for active_connection in self._nm_proxy.ActiveConnections:

            try:
                active_connection_proxy = self._system_bus.get('org.freedesktop.NetworkManager', active_connection)
            except KeyError:
                continue

            if active_connection_proxy.Type in active_connection_types:

                self._active_connection_property_subs.append(
                    active_connection_proxy.PropertiesChanged.connect(self._callback_active_connection))
                self._active_connection_proxies.append(active_connection_proxy)

                for device in active_connection_proxy.Devices:
                    device_proxy = self._system_bus.get('org.freedesktop.NetworkManager', device)
                    self._device_proxies.append(device_proxy)

        # Then update device proxies and status text
        self._update_device_proxies_and_text()

    def _update_device_proxies_and_text(self):
        """Update device proxies and status text"""

        self.text = ''

        for device_proxy in self._device_proxies:

            if device_proxy.State != NM_DEVICE_STATE_ACTIVATED:
                continue

            ip4_config_proxy = self._system_bus.get('org.freedesktop.NetworkManager', device_proxy.Ip4Config)

            if device_proxy.DeviceType == NM_DEVICE_TYPE_ETHERNET:
                if device_proxy.Speed == 0:
                    text = '{}{}: {}{}'.format(self._ethernet_signal_text,
                                               device_proxy.Interface,
                                               ip4_config_proxy.AddressData[0]["address"],
                                               self._spacer)
                    self.text += text

                else:
                    text = '{}{}: {} ({}){}'.format(self._ethernet_signal_text, device_proxy.Interface,
                                                    ip4_config_proxy.AddressData[0]["address"],
                                                    format_bps(device_proxy.Speed),
                                                    self._spacer)
                    self.text += text

            elif device_proxy.DeviceType == NM_DEVICE_TYPE_WIFI:
                active_access_point_proxy = self._system_bus.get('org.freedesktop.NetworkManager',
                                                                 device_proxy.ActiveAccessPoint)

                text = '{}{}: {} ({}){}'.format(self._wifi_signal_text, device_proxy.Interface,
                                                ip4_config_proxy.AddressData[0]["address"],
                                                format_ssid(active_access_point_proxy.Ssid),
                                                self._spacer)
                self.text += text

    def _callback_nm(self, *params):
        """Callback for the PropertiesChanged signal of the NetworkManager proxy"""

        # Don't update if going to sleep
        if inhibit.value:
            return

        # If active connections have changed
        if 'ActiveConnections' in params[1]:
            # Update active connection proxies, device proxies, and status text
            self.update_proxies_and_text()
            self._publish_status()

    def _callback_active_connection(self, *params):
        """Callback for the PropertiesChanged signal of the active connection proxies"""

        # Don't update if going to sleep
        if inhibit.value:
            return

        # If the IPv4 address has changed
        if 'Ip4Config' in params[1] and params[1]['Ip4Config'] != '/':
            # Update device proxies and status text
            self._update_device_proxies_and_text()
            self._publish_status()
