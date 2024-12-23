import os
import configparser
import ast
import sys


# Text to use between components
spacer = ' | '

# Disable if not using statuscmd
enable_signal_text = False

# \x01 to \x04 could be used by statuscolors

network_wifi_signal_text = '\x01'
network_ethernet_signal_text = '\x02'

memory_sys_signal_text = '\x03'
memory_gpu_signal_text = '\x04'

# Interval in seconds between updating memory status
memory_interval = 2.

# Enable using nvidia-smi to get GPU memory usage
memory_enable_gpu = False

volume_sink_signal_text = '\x05'
volume_source_signal_text = '\x06'

# Dictionary of audio sink/source name suffixes to abbreviations
volume_source_sink_abbreviations = {
    'analog-stereo': 'A',  # Internal speaker
    'hdmi-stereo': 'H',  # External (HDMI) speaker
    'a2dp_sink': 'B',  # Bluetooth
    'handsfree_head_unit': 'B',  # Bluetooth
}

# Print audio sink/source names with:
#   import pulsectl
#   pulse = pulsectl.Pulse()
#   print([sink.name for sink in pulse.sink_list()])
#   print([source.name for source in pulse.source_list()])

# Abbreviation to use if a sink/source name suffix isn't found
volume_source_sink_unknown_abbreviation = 'U'

battery_signal_text = '\x07'

# Format string for the date command
date_time_signal_text = '\x08'
date_time_format = '+\"%Y-%m-%d %A %-I:%M %P\"'


# Remove first or last character(s) if they are quotes
def remove_quotes(s):

  if len(s) <= 1:
    return s

  if (s[0] == '\'' and s[-1] == '\'') or (s[0] == '\"' and s[-1] == '\"'):
    s = s[1:-1]

  return s


def load():

    config_file_path = os.path.expanduser('~/.config/blstatus/config.ini')

    # Retrun if there's no user config file
    if not os.path.exists(config_file_path):
        return

    # Load config file
    _config = configparser.ConfigParser()
    _config.read(config_file_path)

    if 'general' in _config:
        if 'spacer' in _config['general']:
            global spacer
            spacer = remove_quotes(_config['general']['spacer'])

        if 'enable_signal_text' in _config['general']:
            global enable_signal_text
            enable_signal_text = _config['general'].getboolean('enable_signal_text')

    if 'network' in _config:
        if 'wifi_signal_text' in  _config['network']:
            global network_wifi_signal_text
            network_wifi_signal_text = remove_quotes(_config['network']['wifi_signal_text'])

        if 'ethernet_signal_text' in  _config['network']:
            global network_ethernet_signal_text
            network_ethernet_signal_text = remove_quotes(_config['network']['ethernet_signal_text'])

    if 'memory' in _config:
        if 'sys_signal_text' in _config['memory']:
            global memory_sys_signal_text
            memory_sys_signal_text = remove_quotes(_config['memory']['sys_signal_text'])

        if 'gpu_signal_text' in _config['memory']:
            global memory_gpu_signal_text
            memory_gpu_signal_text = remove_quotes(_config['memory']['gpu_signal_text'])

        if 'interval' in _config['memory']:
            global memory_interval
            memory_interval = _config['memory'].getfloat('interval')

        if 'enable_gpu' in _config['memory']:
            global memory_enable_gpu
            memory_enable_gpu = _config['memory'].getboolean('enable_gpu')

    if 'volume' in _config:
        if 'sink_signal_text' in _config['volume']:
            global volume_sink_signal_text
            volume_sink_signal_text = remove_quotes(_config['memory']['sink_signal_text'])

        if 'source_signal_text' in _config['volume']:
            global volume_source_signal_text
            volume_source_signal_text = remove_quotes(_config['memory']['source_signal_text'])

        if 'source_sink_abbreviations' in _config['volume']:
            global volume_source_sink_abbreviations
            dict_string = _config['volume']['source_sink_abbreviations']

            try:
                volume_source_sink_abbreviations = ast.literal_eval(dict_string)
            except ValueError:
                print('Unable to create volume_source_sink_abbreviations dictionary from string:', file=sys.stderr)
                print('    ' + dict_string, file=sys.stderr)

        if 'source_sink_unknown_abbreviation' in _config['volume']:
            global volume_source_sink_unknown_abbreviation
            volume_source_sink_unknown_abbreviation = remove_quotes(_config['volume']['source_sink_unknown_abbreviation'])

    if 'battery' in _config:
        if 'signal_text' in _config['battery']:
            global battery_signal_text
            battery_signal_text = remove_quotes(_config['battery']['signal_text'])

    if 'date_time' in _config:
        if 'signal_text' in _config['date_time']:
            global date_time_signal_text
            date_time_signal_text = remove_quotes(_config['battery']['date_time'])

        if 'format' in _config['date_time']:
            global date_time_format
            date_time_format = remove_quotes(_config['date_time']['format'])
