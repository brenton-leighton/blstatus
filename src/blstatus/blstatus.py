#!/usr/bin/env python3

import logging
import threading
import asyncio
import asyncio_glib
import Xlib.display
from apscheduler.schedulers.background import BackgroundScheduler
from pydbus import SystemBus

import blstatus.config as config
import blstatus.inhibit as inhibit

from blstatus.network import Network
from blstatus.memory import Memory
from blstatus.volume import Volume
from blstatus.battery import Battery
from blstatus.date_time import DateTime

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

    global battery, date_time, network, inhibit, scheduler

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

    global lock, network, memory, volume, battery, date_time, root, display

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


def main():

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='/home/brenton/blstatus.log', encoding='utf-8', level=logging.DEBUG)

    logger.debug('Starting blstatus')

    try:

        global login1_proxy, config, network, memory, volume, battery, date_time, scheduler, loop

        login1_proxy = system_bus.get('org.freedesktop.login1')
        login1_proxy.PrepareForSleep.connect(prepare_for_sleep)

        # Load configuration from file if it exists
        config.load()

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

    except:
      logging.exception("Exception")


if __name__ == '__main__':
    main()
