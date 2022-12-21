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
