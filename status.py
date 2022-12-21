#!/usr/bin/env python3

import threading
import asyncio
import asyncio_glib
import Xlib.display
from apscheduler.schedulers.background import BackgroundScheduler
from pydbus import SystemBus

import config
import inhibit

from network import Network
from memory import Memory
from volume import Volume
from battery import Battery
from date_time import DateTime

lock = threading.Lock()

display = Xlib.display.Display()
root = display.screen().root

network = None
memory = None
volume = None
battery = None
date_time = None

scheduler = BackgroundScheduler()
asyncio.set_event_loop_policy(asyncio_glib.GLibEventLoopPolicy())
loop = asyncio.new_event_loop()
system_bus = SystemBus()

login1_proxy = None


def prepare_for_sleep(sleeping):
    if not sleeping:
        # Resuming
        battery.update_text()
        date_time.update_text()
        network.update_proxies_and_text()
        publish()
        inhibit.value = False
        scheduler.resume()
    else:
        # Ignore network signals when going to sleep
        inhibit.value = True
        scheduler.pause()


def publish():
    """Publish status text to root window name"""
    if lock.acquire(blocking=False):
        status_text = ' ' \
                      f'{network.text}' \
                      f'{memory.sys_text}' \
                      f'{memory.gpu_text}' \
                      f'{volume.sink_text}' \
                      f'{volume.source_text}' \
                      f'{battery.text}' \
                      f'{date_time.text}' \
                      ' '

        root.set_wm_name(status_text)
        display.sync()
        lock.release()


if __name__ == '__main__':
    login1_proxy = system_bus.get('org.freedesktop.login1')
    login1_proxy.PrepareForSleep.connect(prepare_for_sleep)

    # The signal text arguments should be empty if not using statuscmd
    network = Network(system_bus, publish, '\x01', '\x02', config.spacer)
    memory = Memory(publish, '\x03', '\x04', config.spacer)
    volume = Volume(loop, publish, '\x05', '\x06', config.spacer)
    battery = Battery(system_bus, publish, '\x07', config.spacer)
    date_time = DateTime(publish, '\x08')

    # Update memory every 2 seconds
    scheduler.add_job(memory.update_and_publish, 'interval', seconds=config.memory_interval)

    # Update date_time on every minute
    scheduler.add_job(date_time.update_and_publish, 'cron', second=0)

    publish()

    scheduler.start()

    loop.run_until_complete(volume.run())
