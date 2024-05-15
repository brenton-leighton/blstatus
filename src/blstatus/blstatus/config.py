import os
import configparser
import ast
import sys


# Text to use between components
spacer = ' | '

# Disable if not using statuscmd
enable_signal_text = False

# Format string for the date command
date_time_format = '+\"%Y-%m-%d %A %-I:%M %P\"'

# Interval in seconds between updating memory status
memory_interval = 2.

# Enable using nvidia-smi to get GPU memory usage
memory_enable_gpu = False

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

    if 'date_time' in _config:
        if 'format' in _config['date_time']:
            global date_time_format
            date_time_format = remove_quotes(_config['date_time']['format'])

    if 'memory' in _config:
        if 'interval' in _config['memory']:
            global memory_interval
            memory_interval = _config['memory'].getfloat('interval')

        if 'enable_gpu' in _config['memory']:
            global memory_enable_gpu
            memory_enable_gpu = _config['memory'].getboolean('enable_gpu')

    if 'volume' in _config:
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
