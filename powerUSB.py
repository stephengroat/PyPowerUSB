#!/usr/bin/env python
# encoding: utf-8

import libPowerUSB
import time
import signal

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-i", "--init", dest="init_watchdog", action="store_true",default=False,
                  help="setup watch dog", metavar="FILE")
parser.add_option("-p", "--period",
                  action="store", type="int",dest="period", default=60,
                  help="watchdog period in seconds (both for init and while loop)")

(options, args) = parser.parse_args()

if options.init_watchdog:
    libPowerUSB.stop_watchdog()
    libPowerUSB.start_watchdog(options.period)

def handle_signals():
    """
    setup signal managers
    """
    signal.signal(signal.SIGINT,libPowerUSB.release)
    signal.signal(signal.SIGTERM,libPowerUSB.release)

handle_signals()

while True:
    libPowerUSB.send_heartbeat()
    time.sleep(options.period)
