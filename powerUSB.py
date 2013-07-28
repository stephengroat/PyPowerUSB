#!/usr/bin/env python
# encoding: utf-8

import libPowerUSB
import time
import signal
import sys

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

def handle_signals(signum=3,func=None):
    """
    signal manager
    """
    libPowerUSB.release()
    sys.exit(0)
signal.signal(signal.SIGINT,handle_signals)
signal.signal(signal.SIGTERM,handle_signals)

handle_signals()

while True:
    libPowerUSB.send_heartbeat()
    time.sleep(options.period)
