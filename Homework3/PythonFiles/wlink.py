# -*- coding: utf-8 -*-
from serial import Serial
from time import sleep

###########################
# serial communication to nexus
def mk_expectation_exception(wanted, got):
    return Exception(
        "Expected {0} but got {1}".format(
            str(wanted),
            str(got)))

class Wlink(object):

    def __init__(self, port, done_callback): #Initialize port

#    TODO: we probably do with the ref to logbroswer

        self.message_buffer = ''
        self.done_callback = done_callback

        self.serial = Serial(port, 9600, timeout=5) #Initialize port with Baud Rate 9600 and timeout of 5s
        print("Giving serial port 2 seconds to wake up")
        sleep(2)
        print("Serial ready")
        print("Reading motor set points")
        connection_established = self.ping()
        if connection_established:
            print("Robot ready")
        else:
            raise mk_expectation_exception("True", "False")


    def __del__(self): #Close port
        self.serial.close()
        print 'Serial port closed'


    def _writemsg(self, msg): #write message to Arduino
        b = msg.encode("ascii") #Format it correctly and...
        print("sending {0}".format(str(b)))
        self.serial.write(b) #... send it after logging it


    def read(self):
        messages = []
        while self.serial.inWaiting():
            byte = self.serial.read()
            if ord(byte) == 131:
                self.done_callback()
            elif ord(byte) == 130:
                messages.append(self.message_buffer)
                self.message_buffer = ''
            else:
                self.message_buffer += byte
            return messages


    def ping(self):
        self._writemsg(":state?;") # Ask for state of the serial connection
        sleep(1) ##########################
        resp = self.read() # Record response
        if 'running\n' in resp:
            return True
        else:
            return False

    #=================================================
    #manual control mode

    def manual_forward(self, power):
        self.control(power, power)
        return

    def manual_backward(self, power):
        self.control(-power, -power)
        return

    def manual_rotateR(self, power):
        self.control(power/2, -power/2)
        return

    def manual_rotateL(self, power):
        self.control(-power/2, power/2)
        return

    def control(self, uleft, uright):
        uleft = int(uleft)
        uright = int(uright)
        msg = ":manual {0:=+04d} {1:=+04d};".format(uleft, uright)
        self._writemsg(msg)
        return

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
        return

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
        return
