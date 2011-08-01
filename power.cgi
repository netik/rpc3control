#!/usr/bin/python

"""

A web interface to control RPC3 outlets 

J. Adams <jna@retina.net>

"""

import cgi
import cgitb
import os

from rpc3Control import *

cgitb.enable()

print "Content-type: text/html\n\n"

RPC=None
RPCUSER=None
RPCPASS=None
TIMEOUT=5

# only these IPs are allowed access. 

WHITELIST=["192.168.2"]

(RPC, RPCUSER, RPCPASS) = load_credentials("/retina/httpd/cgi-bin/.credentials")

r = rpc3Control(RPC, RPCUSER, RPCPASS, False)

def check_access():
    access = False
    for ip in WHITELIST:
        if os.getenv("REMOTE_ADDR").startswith(ip):
            access = True

    if access == False:
        print "Access denied."
        sys.exit(0)


def display_outlets():
    i=1
    while i <= 8:
        (status,name) = r.outlet_status(i)
        print "<TABLE WIDTH=480>"
        print "<TR>"
        print "<TD WIDTH=50%>"
        print "<font size=+2>%d: %s</font>" % (i, name)
        print "</TD><TD WIDTH=50%>"
        print "<INPUT TYPE=\"HIDDEN\" NAME=\"OLDOUTLET-%d\" VALUE=%s>" % (i, ["0","1"][status])

        print "<INPUT TYPE=\"RADIO\" NAME=\"OUTLET-%d\" VALUE=0 %s> Off" % (i, ["CHECKED",""][status])
        print "<INPUT TYPE=\"RADIO\" NAME=\"OUTLET-%d\" VALUE=1 %s> On" % (i, ["","CHECKED"][status])
        print "</TD></TR>"

        i = i + 1 

    print "</TABLE>"
    print "<INPUT TYPE=\"SUBMIT\" NAME=\"SUBMIT\" VALUE=\"Apply\">"

print "<HTML><HEAD>"
print "<TITLE>rpc3 Power Control: %s </TITLE>" % RPC
print '<link rel="stylesheet" href="http://www.retina.net/w/wp-content/themes/hemingway-019/style.css">'

print "</HEAD>"
print "<BODY>"

check_access()

print "<FORM METHOD=POST>"

form = cgi.FieldStorage()

if "SUBMIT" in form:
    i=1
    while i <= 8:
        if form["OLDOUTLET-%d" % i].value != form["OUTLET-%d" % i].value: 
            r.outlet(i, ["off","on"][int(form["OUTLET-%d" % i].value)])
            print "<P>"
            print "Changed Outlet %d" % i 
            print "from %s to %s " % (form["OLDOUTLET-%d" % i].value, form["OUTLET-%d" % i].value)
            print "</P>"
        i = i + 1

print "<P><font size=+3>RPC (%s) at %s</font></p>" % (r.unitid, RPC)
display_outlets()

print "</FORM></BODY></HTML>"
