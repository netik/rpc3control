#!/usr/bin/env python 

"""

check_dsl.py

Check my DSL modem and see if it's still online. 
If it goes down, issue a reboot on the RPC.

Note that this must be run as root. Ping.py requires root to generate
raw sockets.

J. Adams <jna@retina.net>

"""
import syslog
 
from rpc3Control import *
from ping import * 

UPLINK="75.101.56.1"
RPC="192.168.2.5"
OUTLET=5
TIMEOUT=5

syslog.syslog(syslog.LOG_NOTICE, 'Checking network.')

if __name__ == '__main__': 
    if do_one(UPLINK, TIMEOUT) == None:
        # fuck, the network is down!
        syslog.syslog(syslog.LOG_ERR, 'PING FAILED. Rebooting DSL Modem')
        
        r = rpc3Control(RPC)
        r.outlet(OUTLET, 'reboot')
    else:
        syslog.syslog(syslog.LOG_NOTICE, 'Network is up.')




        
