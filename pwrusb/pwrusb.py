import usb

class pyPwrUSB:
    """PowerUSB Control Class

    Example:
        import pwrusb

    """
    __init__(self):
        devPwrUsb=None
        self.handle=None
        busses=usb.busses()
        for bus in busses:
            devices=bus.devices
            for dev in devices:
            if dev.idVendor == 1240 and dev.idProduct == 63:
                devPwrUsb = dev
        if dev is not None:
            self.handle=devPwrUsb.open()
            try:
                self.handle.detachKernelDriver(0)
            except usb.USBError:
                print "handle already detached"
            self.handle.claimInterface(0)
        else:
            raise Exception('Failed to find PowerUSB device')


    PowerUSB_DEVICE_ID = "Vid_04d8&Pid_003F"            # This is the Vendor ID and Product ID for PowerUSB microcontroller

    #BUF_LEN = 256
    BUF_WRT = 64

    # Commands to write to PowerUSB
    ON_PORT1 = 'A'
    OFF_PORT1 = 'B'
    ON_PORT2 = 'C'
    OFF_PORT2 = 'D'
    ON_PORT3 = 'E'
    OFF_PORT3 = 'P'

    DEFON_PORT1 = 'N'
    DEFOFF_PORT1 = 'F'
    DEFON_PORT2 = 'G'
    DEFOFF_PORT2 = 'Q'
    DEFON_PORT3 = 'O'
    DEFOFF_PORT3 = 'H'

    READ_P1 = chr(0xa1)
    READ_P2 = chr(0xa2)
    READ_P3 = chr(0xac)

    READ_P1_PWRUP = chr(0xa3)
    READ_P2_PWRUP = chr(0xa4)
    READ_P3_PWRUP = chr(0xad)

    READ_FIRMWARE_VER = chr(0xa7)
    READ_MODEL = chr(0xaa)

    READ_CURRENT = chr(0xb1)
    READ_CURRENT_CUM = chr(0xb2)
    RESET_CURRENT_COUNT = chr(0xb3)
    WRITE_OVERLOAD = chr(0xb4) #TODO: what is this for ?
    READ_OVERLOAD = chr(0xb5) #TODO: what is this for ?
    SET_CURRENT_RATIO = chr(0xb6) #TODO: what is this for ?
    RESET_BOARD = chr(0xc1) #TODO: what is this for ?
    SET_CURRENT_OFFSET = chr(0xc2) #TODO: what is this for ?

    ALL_PORT_ON = chr(0xa5)
    ALL_PORT_OFF = chr(0xa6)
    SET_MODE = chr(0xa8)
    READ_MODE = chr(0xa9)

    # Digital IO
    SET_IO_DIRECTION = chr(0xd1)
    SET_IO_OUTPUT = chr(0xd3)
    GET_IO_INPUT = chr(0xd4)
    SET_IO_CLOCK = chr(0xd5)
    GET_IO_OUTPUT = chr(0xd6)
    SET_IO_TRIGGER = chr(0xd7)
    SET_IO_SETPLC = chr(0xd8)
    SET_IO_GETPLC = chr(0xd9)
    SET_IO_CLRPLC = chr(0xda)

    # Watchdog
    START_WDT = chr(0x90)
    STOP_WDT = chr(0x91)        
    POWER_CYCLE = chr(0x92)
    READ_WDT = chr(0x93)    #-> return the status.
    HEART_BEAT = chr(0x94)
    SHUTDOWN_OFFON = chr(0x95)

    # Models
    POWERUSB_MODELS={
        0: None,
        1: "Basic",
    2: "Digital IO",
        3: "Watchdog",
        4: "Smart Pro"
        }
    WATCHDOG_STATUS={
        0: "Not running",
        1: "Active",
        2: "Power cycling",
        3: "On but about to do a planned power off",
        4: "Off during planned power off, or not running right after a (planned) power off"
        }

    def send_msg(self,msg):
        padding = chr(0xFF) * (BUF_WRT - len(msg)) #usually, 63 chars
        self,handle.bulkWrite(1,msg+padding,200)

    def _read_msg(self,msg,reply_len):
        send_msg(msg)
        return self.handle.bulkRead(1,64,200)[0:reply_len] #significant reply

    def read_bool(msg):
        thebool=_read_msg(msg,1)[0]
        return bool(thebool)

    def get_ports():
        return read_bool(READ_P1),read_bool(READ_P2), read_bool(READ_P3)

    def get_ports_defaults():
        return read_bool(READ_P1_PWRUP),read_bool(READ_P2_PWRUP), read_bool(READ_P3_PWRUP)

    def read_ints(msg,length):
        return _read_msg(msg,length)

    def read_int(msg,length):
        theints=_read_msg(msg,length)
        offset=0
        result=0
        for theint in theints[::-1]:
        result|= theint << offset
        offset+=8
        return result

    def get_firmware():
        ints=read_ints(READ_FIRMWARE_VER,2)
        return "%d.%d" % (ints[0],ints[1])

    def get_model():
        return POWERUSB_MODELS[read_int(READ_MODEL,1)]

    def get_current():
        return read_int(READ_CURRENT,2) #in milliamps

    def get_total_current():
        total_current = read_int(READ_CURRENT_CUM,4)
        return total_current #in amps/minute

    def reset_total_current():
        send_msg(RESET_CURRENT_COUNT)

    def start_watchdog(expected_interval,allowed_misses=2,offtime=2):
        #expected_interval: seconds between heartbeats (int)
        #allowed_misses: number of consecutive misses allowed 
        #offtime: amount of time to switch off the computer outlet, in seconds (int)
        for param in (expected_interval,allowed_misses,offtime):
        assert type(param) is int
        assert param >= 0
        assert param <= 255
        msg = START_WDT + chr(0) + chr(expected_interval) + chr(allowed_misses) + chr(offtime)
        send_msg(msg)

    def stop_watchdog():
        send_msg(STOP_WDT)

    def get_watchdog_status():
        status = read_int(READ_WDT,1)
        return status,WATCHDOG_STATUS[status]

    def send_heartbeat():
        send_msg(HEART_BEAT)

    def power_cycle_watchdog_port(time_off):
        assert type(time_off) is int
        assert time_off >= 0
        assert time_off <= 255
        msg = POWER_CYCLE + chr(time_off)
        send_msg(msg)

    def planned_poweroff(time_to_off,time_to_on):
        #time_to_off: minutes before turning off the watchdog port, <=255 minutes
        #time_to_on: minutes before turning that port back on <= 720minutes=12 hours. Very imprecise.
        #TODO: check which ports this really aplies to
        for param in (time_to_off,time_to_on):
        assert type(param) is int
        assert param >= 0
        assert time_to_off <= 720
        assert time_to_on <= 255
        time_on_1 = (time_to_on >> 8) & 0x00ff
        time_on_2 = time_to_on & 0x00ff
        msg = SHUTDOWN_OFFON + chr(time_to_off) + chr(time_on_1) + chr(time_on_2)
        send_msg(msg)

    def set_ports(port1=None,port2=None,port3=None):
        msgs=[]
        if port1 is True:
        msgs.append(ON_PORT1) #turn on port 1
        if port1 is False:
        msgs.append(OFF_PORT1) #turn off port 1
        if port2 is True:
        msgs.append(ON_PORT2) #turn on port 2
        if port2 is False:
        msgs.append(OFF_PORT2) #turn off port 2
        if port3 is True:
        msgs.append(ON_PORT3) #turn on port 3
        if port3 is False:
        msgs.append(OFF_PORT3) #turn off port 3
        for msg in msgs:
        send_msg(msg)

    def set_ports_defaults(port1=None,port2=None,port3=None):
        msgs=[]
        if port1 is True:
        msgs.append(DEFON_PORT1) #turn on port 1
        if port1 is False:
        msgs.append(DEFOFF_PORT1) #turn off port 1
        if port2 is True:
        msgs.append(DEFON_PORT2) #turn on port 2
        if port2 is False:
        msgs.append(DEFOFF_PORT2) #turn off port 2
        if port3 is True:
        msgs.append(DEFON_PORT3) #turn on port 3
        if port3 is False:
        msgs.append(DEFOFF_PORT3) #turn off port 3
        for msg in msgs:
        send_msg(msg)

    def __del__(self):
        self.handle.releaseInterface()
