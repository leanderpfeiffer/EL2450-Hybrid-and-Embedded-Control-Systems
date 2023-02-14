# -*- coding: utf-8 -*-
from time import sleep

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

###########################
# serial communication to nexus
def mk_expectation_exception(wanted, got):
    return Exception("Expected {0} but got {1}".format(str(wanted), str(got)))

class Slink(object):
    def __init__(self, socket, logbrowser):
        self.logbrowser=logbrowser # initialiye logbrowser for Serial.print outputs
        self.logbrowser.clear()
        log.info("Giving serial port 2 seconds to wake up")
        sleep(2)
        log.info("Serial ready")
        log.info("Reading motor set points")
        self.socket = socket
        connection_established = self.ping()
        if connection_established:
            log.info("Robot ready")
        else:
            raise mk_expectation_exception("True", "False")

    def __del__(self): #Close port
        print 'Serial port closed'

    def _writemsg(self, msg): #write message from simulation
        b = msg.encode("ascii") #Format it correctly and ...
        log.info("sending {0}".format(str(b)))
        self.socket.send(b) #...send it

    def _readmsg(self): # read a message send by the simulation

#        if flag_serial==0:
#            msgstr=self.socket.recv(256) # receive the message from the simulation
#            self.logbrowser.append(msgstr)
#            msg=b""
#            c=0
#            for a in msgstr:
#                if c==1 and a!=b";":
#                    msg+=a
#                elif c==1 and a==b";":
#                    break
#                if c==0:
#                    if a==b":":
#                        c=1
#        else:
        msg=self.socket.recv(256)
        return msg

    def ping(self):
#        self._readmsg()
#        self._writemsg(":state?;") # Ask for states/the control input
#        # sleep(0.5) ##########################
#
#        resp = self._readmsg(0) # Record response
#        if not resp.startswith(b"state"):
#            self.control(0,0)
#            raise mk_expectation_exception(b"state", resp)
#        _, left, right = resp.decode("ascii").split(" ")
#        return int(left), int(right)

        #self._readmsg(0) # read out possible old buffer values
        self._writemsg(":state?;") # Ask for state of the serial connection
        #sleep(1) ##########################
        resp = self._readmsg() # Record response
        self.logbrowser.append(resp)
        if resp!= "":
            return True
        else:
            return False

     #=================================================
    #manual control mode

    def manual_forward(self, power):
        assert power >= -999 and power <= 999
        serialprint_msg = self.control(power, power)
        return serialprint_msg

    def manual_backward(self, power):
        assert power >= -999 and power <= 999
        serialprint_msg = self.control(-power, -power)
        return serialprint_msg

    def manual_rotateR(self, power):
        assert power >= -999 and power <= 999
        serialprint_msg = self.control(power/2, -power/2)
        return serialprint_msg

    def manual_rotateL(self, power):
        assert power >= -999 and power <= 999
        serialprint_msg = self.control(-power/2, power/2)
        return serialprint_msg

    def control(self, uleft, uright):
        assert uleft >= -999 and uleft <= 999
        assert uright >= -999 and uright <= 999
        # NOTE: a constant base voltage may be needed.
        uleft = int(uleft)
        uright = int(uright)
        msg = ":manual {0:=+04d} {1:=+04d};".format(uleft, uright)
        #print msg
        self._writemsg(msg)
        #for printing serial.print into the GUI
        serialprint_msg=self._readmsg()
        self.logbrowser.append(serialprint_msg)
        return serialprint_msg

    #===============================================
    #send state

    def transmit_state(self, x, y, theta):
        # transform x, y, theta to int
        # assume x,y are in meters, send them in cm
        x = int(x*100)
        y = int(y*100)
        # assume theta is given in degree
        theta = int(theta)
        msg = ":pose {0:=+04d} {1:=+04d} {2:=+04d};".format(x, y, theta)
        print msg
        self._writemsg(msg)
        #for printing serial.print into the GUI
        serialprint_msg=self._readmsg()
        self.logbrowser.append(serialprint_msg)
        return serialprint_msg

    #===============================================
    #send start and goal point

    def transmit_startgoal(self, x0, y0, xg, yg):
        # transform x0, y0, xg, yg, to int
        # assume x,y are in meters, send them in cm
        x0 = int(x0*100)
        y0 = int(y0*100)
        xg = int(xg*100)
        yg = int(yg*100)
        msg = ":startgoal {0:=+04d} {1:=+04d} {2:=+04d} {3:=+04d};".format(x0, y0, xg, yg)
        print msg
        self._writemsg(msg)
        #for printing serial.print into the GUI
        serialprint_msg=self._readmsg()
        self.logbrowser.append(serialprint_msg)
        return serialprint_msg
