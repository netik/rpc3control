#!/usr/bin/python

"""

Control Class for the Baytech RPC3 
J. Adams <jna@retina.net>

"""

from pexpect import *
import sys
import re
import syslog

class rpc3ControlError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class rpc3Control:
    """ Class to control a Baytech RPC-3 """

    child = None
    status = {} 
    name = {}
    statuscached = False
    unitid = ""

    def __init__(self, hostname, user=None, password=None, debug=False):
        self.hostname = hostname
        self.user = user
        self.password = password
        self.debug = debug
        self.connect()
        self.unitid = ""

        """
        the RPC supports username, or password, or both 
        so we support both of those cases in this code. 
        """

        """ get unit id """
        self.child.expect([".*Unit ID: (.*)", EOF, TIMEOUT]) 
        self.unitid = self.child.match.group(1)
        
        if user != None:
            self.es("Enter username>", user)

        if password != None:
            self.es("Enter password>", password)

    def es(self,str_expect,str_send):
        """ 
        a pexpect helper method; expect and send with error monitoring
        """

        result = self.child.expect([str_expect, EOF, TIMEOUT])

        if result == 0: 
            self.child.send("%s\r" % str_send)
            return 
        
        if result > 0:
            if result == 1: 
                raise rpc3ControlError("EOF during read")
            else:
                raise rpc3ControlError("Timeout during read")

    def connect(self):
        if self.child == None:
            self.child = spawn("telnet " + self.hostname)
            result = self.child.expect(["Connected to", EOF, TIMEOUT])
            self.child.send("\r")

        if self.debug == True:
            self.child.logfile = sys.stdout

    def outlet(self,outlet_number,state):
        """
        control an outlet 
        state is one of "on","off",or "reboot"
        outlet_number is an integer. 
        """

        if state not in ("on", "off", "reboot"):
            raise rpc3ControlError('Invalid outlet state')

        if int(outlet_number) > 8 or int(outlet_number) < 1:
            return None
        
        self.es("Enter Selection>", "1")
        self.es("RPC-3>", "%s %d\rY"  % (state, outlet_number) )
        self.es("RPC-3>", "MENU")

        self.statuscached = False

        return True

    def outlet_status(self, outlet_number, ignore_cache = False):
        """ Get the status of an outlet """
        
        if self.statuscached == True and ignore_cache != True:
            return (self.status[outlet_number],self.name[outlet_number])

        if int(outlet_number) > 8 or int(outlet_number) < 1:
            return None

        self.es("Enter Selection>", "1")
        self.es("RPC-3>", "MENU")

        # parse the output
        inlist = False

        for line in self.child.before.split('\n'):
            if line.rstrip() == "" and inlist:
                inlist = False

            if inlist:
                m = re.match('^ .....([0-9]) ..... (...........) ([0-9]) ..... (On|Off)',line)
                
                self.name[int(m.group(1))] = m.group(2).rstrip()

                if m.group(4) == "On":
                    self.status[int(m.group(1))] = True
                else:
                    self.status[int(m.group(1))] = False

            if line.find("Status") != -1:
                inlist = True

        self.statuscached = True
        return (self.status[outlet_number],self.name[outlet_number])

# fetch credentials
# the credentials should be in a file called ".credentials" and in the form "hostname:user:pass" on one line. 
def load_credentials(credentials = ".credentials" ):
    user = None
    pw = None
    rpc = None
    err = None
    whitelist = None

    try:
        f = open(credentials, 'r')
        (rpc, user, pw, w) = f.readline().rstrip().split(":",3)
        whitelist = w.split(",")
        f.close()
    except IOError:
        err = "FATAL: Couldn't open credentials file"
    except ValueError:
        err = "FATAL: Malformed %s file. Credentails should be in the form \"host:user:pw\"" % credentials

    if err != None:
        syslog.syslog(syslog.LOG_ERR, err)
        print >> sys.stderr, err
        sys.exit(1)

    return (rpc,user,pw,whitelist)
