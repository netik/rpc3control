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
import sys
 
from rpc3Control import *
from ping import * 

UPLINK="75.101.56.1" 
RPC=None
RPCUSER=None
RPCPASS=None
OUTLET=5
TIMEOUT=3
CNT=3

(RPC, RPCUSER, RPCPASS, WHITELIST) = load_credentials("/retina/check_dsl/.credentials")

# syslog.syslog(syslog.LOG_NOTICE, 'Checking network.')

if __name__ == '__main__': 
    count = 1
    while (count < (CNT+1)): 
        syslog.syslog(syslog.LOG_NOTICE, "Checking DSL... Try #%d" % count)
        result = do_one(UPLINK, TIMEOUT)

        if result != None:
            # we're good. 
            syslog.syslog(syslog.LOG_NOTICE, "PING OK. Try #%d" % count)
            sys.exit(0)

        syslog.syslog(syslog.LOG_NOTICE, "PING FAILED. Try #%d" % count)
        count += 1

    # fuck, the network is down!
    syslog.syslog(syslog.LOG_NOTICE, 'PING FAILED. Rebooting DSL Modem')
        
    r = rpc3Control(RPC, RPCUSER, RPCPASS, False)
    r.outlet(OUTLET, 'reboot')

    syslog.syslog(syslog.LOG_NOTICE, 'Reboot complete.')
    sys.exit(1)
