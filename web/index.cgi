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

print "Content-type: text/html"

RPC=None
RPCUSER=None
RPCPASS=None
TIMEOUT=5

(RPC, RPCUSER, RPCPASS, WHITELIST) = load_credentials("/retina/httpd/htdocs/power/.credentials")

r = rpc3Control(RPC, RPCUSER, RPCPASS, False)

def check_access():
    access = False
    for ip in WHITELIST:
        if os.getenv("REMOTE_ADDR").startswith(ip):
            access = True

    if access == False:
        print "Status: 403\nContent-Type:text/html\n\n"
        print "Access denied from %s." % os.getenv("REMOTE_ADDR")
        sys.exit(0)

def display_reboots():

    i=1

    print "<H2>%s (%s)</H2>" % (r.unitid, RPC)
    print "<UL class=\"edit rounded\">"
    while i <= 8:
        (status,name) = r.outlet_status(i)
        print "<li><a needconfirm=\"yes\" href=\"index.cgi?reboot=%d\">Reboot %d: %s</a></li>" % (i, i, name)
        i = i + 1 
    print "</UL>"

def display_outlets():

    i=1

#    print "<H2>%s (%s) Outlet Status/Toggle</H2>" % (r.unitid, RPC)
    print "<UL class=\"edit rounded\">"
    while i <= 8:
        (status,name) = r.outlet_status(i)
        print "<li>%d: %s" % (i, name)
        print "<span class=\"toggle\">"
        print "<INPUT TYPE=\"CHECKBOX\" NAME=\"OUTLET-%d\" VALUE=1 %s >" % (i, ["","CHECKED"][status])
        print "</span></li>"

        print "<INPUT TYPE=\"HIDDEN\" NAME=\"OLDOUTLET-%d\" VALUE=%s>" % (i, ["0","1"][status])
#        print "<INPUT TYPE=\"RADIO\" NAME=\"OUTLET-%d\" VALUE=0 %s > Off" % (i, ["CHECKED",""][status])
#        print "<INPUT TYPE=\"RADIO\" NAME=\"OUTLET-%d\" VALUE=1 %s > On" % (i, ["","CHECKED"][status])
#        print "<INPUT TYPE=\"RADIO\" NAME=\"OUTLET-%d\" VALUE=2> Reboot" %i

        i = i + 1 
    print "</UL>"

    print '<a style="margin-top: 10px; margin-bottom: 10px; color:rgba(0,0,0,.9)" onclick="document.powerForm.submit()" href="#" class="submit whiteButton">Submit</a>'

check_access()

print "Content-type: text/html\n\n"
print """

<!doctype html>
<html>
    <head>
        <meta charset="UTF-8" />
        
        <title>RPC3 Control</title>
        <style type="text/css" media="screen">@import "css/jqtouch.css";</style>
        <script src="js/jquery-1.7.js" type="text/javascript" charset="utf-8"></script>
        <script src="js/jqtouch-jquery.min.js" type="text/javascript" charset="utf-8"></script>
        <script src="js/jqtouch.js" type="text/javascript" charset="utf-8"></script>
        <script type="text/javascript" charset="utf-8">
            var jQT = new $.jQTouch({
                icon: 'jqtouch.png',
                addGlossToIcon: false,
                startupScreen: 'jqt_startup.png',
                statusBar: 'black'
            });

            $(function(){
                // Custom Javascript (onReady)
                $('a[needconfirm="yes"]').bind('click', function() {
                    if (confirm('Confirm reboot?')) {
                        return true;
                    } else {
                        return false;
                    }
                });
            });
        </script>
        <style type="text/css" media="screen">
            /* Custom Style */
        </style>
    </head>
    <body>
        <div id="jqt">

"""

form = cgi.FieldStorage()
print "<FORM METHOD=\"POST\" ACTION=\"index.cgi\" id=\"powerForm\" name=\"powerForm\">"
print '<div class="toolbar">'
print "<H1>RPC3 Control</font></h1>"
print """
                    <a href="#" class="back">Back</a>
                </div>
"""

if os.getenv('REQUEST_METHOD') == "POST":
    i=1
    print "<UL>"
    while i <= 8:
#        print "%d: old: %s " % (i,form.getvalue("OLDOUTLET-%d" % i))
#        print "%d: new: %s<BR> " % (i,form.getvalue("OUTLET-%d" % i))
        
        if (form.getvalue("OLDOUTLET-%d" % i) or "0") != (form.getvalue("OUTLET-%d" % i) or "0"):
            r.outlet(i, ["off","on", "reboot"][int((form.getvalue("OUTLET-%d" % i) or "0"))])
            print "<B>Outlet %d</B>: %s<BR>" % (i,["turned off", "turned on", "rebooted"][int((form.getvalue("OUTLET-%d" % i) or "0"))])
        i = i + 1

display_reboots()
display_outlets()

print """   </FORM>
            </div>
        </div>
    </body>
</html>
"""
