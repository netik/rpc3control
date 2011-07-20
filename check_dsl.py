#!/usr/bin/env python 

"""

Check my DSL modem and see if it's still online. 

If it goes down, issue a reboot on the RPC.

J. Adams <jna@retina.net>

"""
import syslog
 
from rpc3Control import *
from ping import * 

UPLINK="75.101.56.99"
RPC="192.168.2.5"
OUTLET=5
TIMEOUT=5

syslog.syslog(syslog.LOG_NOTICE, 'Checking network.')

sys.exit(0)


if __name__ == '__main__': 
    if do_one(UPLINK, TIMEOUT) == None:
        # fuck, the network is down!
        syslog.syslog(syslog.LOG_ERR, 'PING FAILED. Rebooting DSL Modem')
        
        r = rpc3Control(RPC)
        r.outlet(OUTLET, 'reboot')
    else:
        syslog.syslog(syslog.LOG_NOTICE, 'Network is up.')




        
