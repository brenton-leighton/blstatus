# blstatus

A status monitor for [DWM](https://dwm.suckless.org/) (or any window manager that uses WM_NAME to fill a status bar).
Compared to [slstatus](https://tools.suckless.org/slstatus/), blstatus is capable of displaying more information, and it also updates network, audio volume, and battery information asynchronously, rather than using polling.

![Example status_bar](https://github.com/brenton-leighton/blstatus/assets/12228142/0365ec84-96be-4532-a193-5c8ddba88a34)

## Installation

blstatus has the following dependencies:

- apscheduler
- asyncio-glib
- pulsectl-asyncio
- pydbus
- xlib

The package can be installed using [pipx](https://pipx.pypa.io/stable/installation/):

```bash
pipx install blstatus
```

## Configuration

blstatus can be configured with a file located at `~/.config/blstatus/config.ini`, e.g.

```ini
[general]
# Text to use between components
# Needs to be quoted if spaces (or a quote character) are used
spacer = ' | '

# Enable if using statuscmd (https://dwm.suckless.org/patches/statuscmd/)
enable_signal_text = false

[date_time]
# Format string for the date command
# Must be quoted and % must be doubled
format = '+"%%Y-%%m-%%d %%A %%-I:%%M %%P"'

[memory]
# Interval in seconds between updating memory status
interval = 2.0

# Enable using nvidia-smi to get GPU memory usage
enable_gpu = false

[volume]
# Dictionary to map a PulseAudio sink/source name to an abbreviation
# If the end of a PulseAudio device name matches a key the value will be used
# If a PulseAudio device name doesn't match anything in the dictionary, source_sink_unknown_abbreviation is used
# Must be a single line
source_sink_abbreviations = { 'analog-stereo': 'A', 'hdmi-stereo': 'H', 'a2dp_sink': 'B', 'handsfree_head_unit': 'B' }

# Abbreviation to use if a sink/source name isn't known
source_sink_unknown_abbreviation = 'U'
```

To determine the key part of `source_sink_abbreviations`, PulseAudio sink/source names can be printed with:

```python
import pulsectl

pulse = pulsectl.Pulse()
print([sink.name for sink in pulse.sink_list()])
print([source.name for source in pulse.source_list()])
```
