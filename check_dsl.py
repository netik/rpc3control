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
RPCUSER=None
RPCPASS=None
OUTLET=5
TIMEOUT=5

# fetch credentials
# the credentials should be in a file called ".credentials" and in the form "user:pass" on one line. 
def load_credentials():
    user = None
    pw = None

    try:
        f = open('.credentialxxs', 'r')
        credentials = f.readline().rstrip().split(":")
        user=credentials[0]
        pw=credentials[1]
        f.close()
    except IOError:
        user=None
        pw=None
    except IndexError:
        syslog.syslog(syslog.LOG_ERR, 'Malformed Credentials file')
        user=None
        pw=None

    return (user,pw)

(RPCUSER, RPCPASS) = load_credentials()

syslog.syslog(syslog.LOG_NOTICE, 'Checking network.')

if __name__ == '__main__': 
    if do_one(UPLINK, TIMEOUT) == None:
        # fuck, the network is down!
        syslog.syslog(syslog.LOG_ERR, 'PING FAILED. Rebooting DSL Modem')
        
        r = rpc3Control(RPC,RPCUSER,RPCPASS)
        r.outlet(OUTLET, 'reboot')

        syslog.syslog(syslog.LOG_ERR, 'Reboot complete.')
    else:
        syslog.syslog(syslog.LOG_NOTICE, 'Network is up.')
