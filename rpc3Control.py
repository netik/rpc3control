#!/usr/bin/python

'''

Control Class for the Baytech RPC3 
J. Adams <jna@retina.net>

'''

from pexpect import *
import sys

class rpc3ControlError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class rpc3Control:
    ''' Class to control a Baytech RPC-3   '''

    child = None

    def __init__(self, hostname, user=None, password=None, debug=False):
        self.hostname = hostname
        self.user = user
        self.password = password
        self.debug = debug
        self.connect()

        '''
        the RPC supports username, or password, or both 
        so we support both of those cases in this code. 
        '''

        if user != None:
            self.es("Enter username>", user)

        if password != None:
            self.es("Enter password>", password)

    def es(self,str_expect,str_send):
        ''' 
        a pexpect helper method; expect and send with error monitoring
        '''

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

        if self.debug == True:
            self.child.logfile = sys.stdout

    def outlet(self,outlet_number,state):
        '''
        control an outlet 
        state is one of "on","off",or "reboot"
        outlet_number is an integer. 
        '''

        if state not in ("on", "off", "reboot"):
            raise rpc3ControlError('Invalid outlet state')

        if int(outlet_number) > 8 or int(outlet_number) < 1:
            return None
        
        self.es("Enter Selection>", "1")
        self.es("RPC-3>", "%s %d\rY"  % (state, outlet_number) )
        self.es("RPC-3>", "MENU")

        return True

    def outlet_status(self, outlet_number):
        ''' Get the status of an outlet '''

        if int(outlet_number) > 8 or int(outlet_number) < 1:
            return None

        self.es("Enter Selection>", "1")
        self.es("RPC-3>", "MENU")

        # parse the output
        inlist = False
        status = {}

        for line in self.child.before.split('\n'):
            if line.rstrip() == "" and inlist:
                inlist = False

            if inlist:
                words = line.split()
                if words[3] == "On":
                    status[int(words[0])] = True
                else:
                    status[int(words[0])] = False

            if line.find("Status") != -1:
                inlist = True

        return status[outlet_number]







