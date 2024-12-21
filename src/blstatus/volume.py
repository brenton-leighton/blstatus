from typing import Callable
import signal
import asyncio
from contextlib import suppress
import pulsectl_asyncio

import blstatus.config as config
import blstatus.inhibit as inhibit


def get_abbreviation(name: str) -> str:
    for key, value in config.volume_source_sink_abbreviations.items():
        if name.endswith(key):
            return value

    return config.volume_source_sink_unknown_abbreviation


class Volume:
    _loop = None
    _publish_status = None
    _sink_signal_text = ''
    _source_signal_text = ''
    _spacer = ''
    sink_text = '- / '
    source_text = '- | '

    def __init__(self, loop, publish_status: Callable[[], None], spacer=''):
        self._loop = loop
        self._publish_status = publish_status
        self._sink_signal_text = config.volume_sink_signal_text if config.enable_signal_text else ''
        self._source_signal_text = config.volume_source_signal_text if config.enable_signal_text else ''
        self._spacer = spacer

    def _update_sink_text(self, sink):
        sink_abbreviation = get_abbreviation(sink.name)

        if sink.mute:
            self.sink_text = '{}{}: 0% / '.format(self._sink_signal_text, sink_abbreviation)
        else:
            self.sink_text = '{}{}: {:.0f}% / '.format(self._sink_signal_text, sink_abbreviation,
                                                       sink.volume.value_flat * 100.)

    def _update_source_text(self, source):
        source_abbreviation = get_abbreviation(source.name)

        if source.mute:
            self.source_text = '{}{}: 0%{}'.format(self._source_signal_text, source_abbreviation, self._spacer)
        else:
            self.source_text = '{}{}: {:.0f}%{}'.format(self._source_signal_text, source_abbreviation,
                                                        source.volume.value_flat * 100., self._spacer)

    async def _listen(self, pulse: pulsectl_asyncio.PulseAsync):
        async for event in pulse.subscribe_events('server', 'sink', 'source'):

            # Don't update if going to sleep
            if inhibit.value:
              continue

            # Ignore anything but change events
            if event.t != 'change':
                continue

            server_info = await pulse.server_info()

            # Update sink for server or sink event
            if event.facility != 'source':
                default_sink = await pulse.get_sink_by_name(server_info.default_sink_name)
                self._update_sink_text(default_sink)

            # Update source for server or source event
            if event.facility != 'sink':
                default_source = await pulse.get_source_by_name(server_info.default_source_name)
                self._update_source_text(default_source)

            self._publish_status()

    async def run(self):
        async with pulsectl_asyncio.PulseAsync('status-bar-volume') as pulse:
            # First update
            server_info = await pulse.server_info()

            default_sink = await pulse.get_sink_by_name(server_info.default_sink_name)
            self._update_sink_text(default_sink)

            default_source = await pulse.get_source_by_name(server_info.default_source_name)
            self._update_source_text(default_source)

            # Create listen task
            listen_task = asyncio.create_task(self._listen(pulse))

            # Handle signals
            for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
                self._loop.add_signal_handler(sig, listen_task.cancel)

            with suppress(asyncio.CancelledError):
                await listen_task
