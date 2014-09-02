PyPowerUSB
==========

Python tools to command PowerUSB plugs. As of now, this consists of :
- a library which is Python 2.5 compatible, and confirmed to work when controlled from a Synology workstation with the python 2.5 default package. The library provides all known messages of the proprietary protocol used, and each function available on the watchdog flavor of the powerUSB plug was tested.
- a basic runner which only starts up the watchdog functionality. However, this could be easily extended for diverse use cases.
