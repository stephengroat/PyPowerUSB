import usb


class PyPwrUSB:
    """PowerUSB Control Class

    Example:
        import pwrusb

        pwrusb=pwrusb.pyPwrUSB()
        pwrusb.set_port(1, 'ON')
        pwrusb.set_port(2, 'OFF', default=True)
        print pwr.get_firmware()

    """

    def __init__(self):
        devpwrusb = None
        self.handle = None
        busses = usb.busses()
        for bus in busses:
            devices = bus.devices
            for dev in devices:
                if dev.idVendor == 1240 and dev.idProduct == 63:
                    devpwrusb = dev
        if devpwrusb is not None:
            self.handle = devpwrusb.open()
            # try:
            #    self.handle.detachKernelDriver(0)
            # except usb.USBError:
            #    print "handle already detached"
            self.handle.claimInterface(0)
        else:
            raise Exception('Failed to find PowerUSB device')

    PowerUSB_DEVICE_ID = "Vid_04d8&Pid_003F"  # This is the Vendor ID and Product ID for PowerUSB microcontroller

    # BUF_LEN = 256
    BUF_WRT = 64

    # Commands to write to PowerUSB
    commands = {
        'SET_PORT_ALL_ON': chr(0xa5),
        'SET_PORT_ALL_OFF': chr(0xa6),

        'SET_PORT1_ON': 'A',
        'SET_PORT1_OFF': 'B',
        'SET_PORT2_ON': 'C',
        'SET_PORT2_OFF': 'D',
        'SET_PORT3_ON': 'E',
        'SET_PORT3_OFF': 'P',

        'SET_PORT1_DEFAULT_ON': 'N',
        'SET_PORT1_DEFAULT_OFF': 'F',
        'SET_PORT2_DEFAULT_ON': 'G',
        'SET_PORT2_DEFAULT_OFF': 'Q',
        'SET_PORT3_DEFAULT_ON': 'O',
        'SET_PORT4_DEFAULT_OFF': 'H',

        'READ_P1': [chr(0xa1), bool],
        'READ_P2': [chr(0xa2), bool],
        'READ_P3': [chr(0xac), bool],

        'READ_P1_PWRUP': [chr(0xa3), bool],
        'READ_P2_PWRUP': [chr(0xa4), bool],
        'READ_P3_PWRUP': [chr(0xad), bool],

        'READ_FIRMWARE_VER': [chr(0xa7), int, 2],
        'READ_MODEL': [chr(0xaa), int, 1],

        'READ_CURRENT': [chr(0xb1), int, 2],
        'READ_CURRENT_CUM': [chr(0xb2), int, 4],
        'RESET_CURRENT_COUNT': chr(0xb3),
        
        'SET_MODE': chr(0xa8),
        'READ_MODE': chr(0xa9),

        # Digital IO
        'SET_IO_DIRECTION': chr(0xd1),
        'SET_IO_OUTPUT': chr(0xd3),
        'GET_IO_INPUT': chr(0xd4),
        'SET_IO_CLOCK': chr(0xd5),
        'GET_IO_OUTPUT': chr(0xd6),
        'SET_IO_TRIGGER': chr(0xd7),
        'SET_IO_SETPLC': chr(0xd8),
        'SET_IO_GETPLC': chr(0xd9),
        'SET_IO_CLRPLC': chr(0xda),

        # Watchdog
        'START_WDT': chr(0x90),
        'STOP_WDT': chr(0x91),
        'POWER_CYCLE': chr(0x92),
        'READ_WDT': [chr(0x93), int, 1]  # -> return the status.
        'HEART_BEAT': chr(0x94),
        'SHUTDOWN_OFFON': chr(0x95)
    }

    WRITE_OVERLOAD = chr(0xb4)  # TODO: what is this for ?
    READ_OVERLOAD = chr(0xb5)  # TODO: what is this for ?
    SET_CURRENT_RATIO = chr(0xb6)  # TODO: what is this for ?
    RESET_BOARD = chr(0xc1)  # TODO: what is this for ?
    SET_CURRENT_OFFSET = chr(0xc2)  # TODO: what is this for ?

    # Models
    POWERUSB_MODELS = {
        0: None,
        1: "Basic",
        2: "Digital IO",
        3: "Watchdog",
        4: "Smart Pro"
    }
    WATCHDOG_STATUS = {
        0: "Not running",
        1: "Active",
        2: "Power cycling",
        3: "On but about to do a planned power off",
        4: "Off during planned power off, or not running right after a (planned) power off"
    }

    def _send_msg(self, msg):
        padding = chr(0xFF) * (self.BUF_WRT - len(msg))  # usually, 63 chars
        self.handle.bulkWrite(0x01, msg + padding, 200)

    def _read_msg(self, msg, reply_len):
        self._send_msg(msg)
        return self.handle.bulkRead(0x81, 64, 200)[0:reply_len]  # significant reply

    def _read_bool(self, msg):
        return bool(self._read_msg(msg, 1)[0])

    #TODO: Combine _read_ints and _read_int
    def _read_ints(self, msg, length):
        return self._read_msg(msg, length)

    #TODO: Combine _read_ints and _read_int
    def _read_int(self, msg, length):
        vals = self._read_msg(msg, length)
        offset = 0
        result = 0
        for val in vals[::-1]:
            result |= val << offset
            offset += 8
        return result

    def _read(self, msg):
        if msg not in self.commands:
            raise Exception('Invalid message')
        if self.commands[msg][1] == bool:
            return self._read_bool(msg[0])
        elif self.commands[msg][1] == int:
            return self._read_int(msg[0], self.commands[msg][2])

    def get_port(self, port_number, default=False):
        if 1 <= port_number < 3:
            raise Exception('Invalid port number')
        if default:
            return self._read(self.commands['READ_P' + port_number + '_PWRUP'])
        else:
            return self._read(self.commands['READ_P' + port_number])

    def get_firmware(self):
        ints = self._read_ints(self.commands['READ_FIRMWARE_VER'], 2)
        return "%d.%d" % (ints[0], ints[1])

    def get_model(self):
        return self.POWERUSB_MODELS[self._read(self.commands['READ_MODEL'])]

    def get_current(self):
        return self._read(self.commands['READ_CURRENT'])  # in milliamps

    def get_total_current(self):
        return self._read(self.commands['READ_CURRENT_CUM'])  # in amps/minute

    def reset_total_current(self):
        self._send_msg(self.commands['RESET_CURRENT_COUNT'])

    def start_watchdog(self, expected_interval, allowed_misses=2, offtime=2):
        # expected_interval: seconds between heartbeats (int)
        # allowed_misses: number of consecutive misses allowed
        # offtime: amount of time to switch off the computer outlet, in seconds (int)
        for param in (expected_interval, allowed_misses, offtime):
            assert type(param) is int
            assert param >= 0
            assert param <= 255
        self._send_msg(self.commands['START_WDT'] + chr(0) + chr(expected_interval) + chr(allowed_misses) + chr(offtime))

    def stop_watchdog(self):
        self._send_msg(self.commands['STOP_WDT'])

    def get_watchdog_status(self):
        status = self._read(self.commands['READ_WDT'])
        if status not in self.WATCHDOG_STATUS:
            raise Exception('Invalid watchdog status')
        else
            return self.WATCHDOG_STATUS[status]

    def send_heartbeat(self):
        self._send_msg(self.commands['HEART_BEAT'])

    def power_cycle_watchdog_port(self, time_off):
        assert type(time_off) is int and 0 <= time_off <= 255
        self._send_msg(self.commands['POWER_CYCLE'] + chr(time_off))

    def planned_poweroff(self, time_to_off, time_to_on):
        # time_to_off: minutes before turning off the watchdog port, <=255 minutes
        # time_to_on: minutes before turning that port back on <= 720minutes=12 hours. Very imprecise.
        # TODO: check which ports this really aplies to
        for param in (time_to_off, time_to_on):
            assert type(param) is int
            assert param >= 0
        assert time_to_off <= 720
        assert time_to_on <= 255
        time_on_1 = (time_to_on >> 8) & 0x00ff
        time_on_2 = time_to_on & 0x00ff
        self._send_msg(self.commands['SHUTDOWN_OFFON'] + chr(time_to_off) + chr(time_on_1) + chr(time_on_2))

    def set_port(self, port_number, status, default=False):
        if 1 <= port_number < 3:
            raise Exception('Invalid port number')
        if status not in ['ON', 'OFF']:
            raise Exception('Invalid status')
        if default:
            return self._send_msg(self.commands['SET_PORT' + port_number + '_DEFAULT_' + status])
        else:
            return self._send_msg(self.commands['SET_PORT' + port_number + '_' + status])

    def __del__(self):
        self.handle.releaseInterface()
