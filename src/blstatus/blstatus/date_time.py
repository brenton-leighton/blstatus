from typing import Callable
import subprocess

import blstatus.config as config
import blstatus.inhibit as inhibit


class DateTime:
    _publish_status = None
    _signal_text = ''
    _spacer = ''
    text = ''

    def __init__(self, publish_status: Callable[[], None], signal_text='', spacer=''):
        self._publish_status = publish_status
        self._signal_text = signal_text if config.enable_signal_text else ''  # statuscmd signal text
        self._spacer = spacer
        self.update_text()

    def update_text(self):
        """Update the date/time status text"""

        # Run the date command to get the date/time text
        self.text = '{}{}{}'.format(self._signal_text,
                                    subprocess.run(['date', config.date_time_format],
                                                   capture_output=True,
                                                   text=True).stdout[1:-2], self._spacer)

    def update_and_publish(self):
        """Callback for the scheduler job"""

        # Don't update if going to sleep
        if inhibit.value:
            return

        self.update_text()
        self._publish_status()
