from typing import Callable
import subprocess

import blstatus.config as config
import blstatus.inhibit as inhibit


def format_mebibyte(value):
    if value < 1024:
        return ''.join([str(round(value, 1)) + ' MiB'])
    else:
        return ''.join([str(round((value / 1024), 1)) + ' GiB'])


class Memory:
    _publish_status = None
    _sys_signal_text = ''
    _gpu_signal_text = ''
    _spacer = ''
    sys_text = ''
    gpu_text = ''

    def __init__(self, publish_status: Callable[[], None], spacer=''):
        self._publish_status = publish_status
        self._sys_signal_text = config.memory_sys_signal_text if config.enable_signal_text else ''  # statuscmd signal text
        self._gpu_signal_text = config.memory_gpu_signal_text if config.enable_signal_text else ''
        self._spacer = spacer
        self._update_text()

    def _update_text(self):
        """Update system and GPU memory status text"""

        # System memory
        sys_mem_used = format_mebibyte(
            int(subprocess.run(['free', '-m'],
                               capture_output=True,
                               text=True).stdout.split('\n')[1].split()[2]))

        self.sys_text = '{}sys {}{}'.format(self._sys_signal_text, sys_mem_used, self._spacer)

        # GPU (NVIDIA) memory
        if config.memory_enable_gpu:
            try:
                gpu_mem_used = format_mebibyte(
                    int(subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader'],
                                       capture_output=True,
                                       text=True).stdout[:-5]))

                self.gpu_text = '{}gpu {}{}'.format(self._gpu_signal_text, gpu_mem_used, self._spacer)

            except FileNotFoundError:
                self.gpu_text = ''
            except ValueError:
                self.gpu_text = ''

    def update_and_publish(self):
        """Callback for the scheduler job"""

        # Don't update if going to sleep
        if inhibit.value:
            return

        self._update_text()
        self._publish_status()
