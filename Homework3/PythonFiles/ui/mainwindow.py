# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QFileDialog
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtCore import QTimer
import PyQt4.QtCore
import math

# import for socket creation
import socket
import sys
import select

from Ui_mainwindow import Ui_MainWindow

import corridor_projection, mocap, wlink, time, slink, mocapSIM

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        #create timer which are used for periodic execution of controlupdate and mocapupdate
        self.controllooptimer = QTimer()
        self.controllooptimer.timeout.connect(self.controlupdate)
        self.mocaplooptimer = QTimer()
        self.mocaplooptimer.timeout.connect(self.mocapupdate)
        self.serialreadtimer = QTimer()
        self.serialreadtimer.timeout.connect(self.readserial)
        
        self.serialreadHz = 100
        
        #display animation
        self.animation = corridor_projection.corridor_animation()
        
        # conversion factor from mocap measurements to screen pixels
        self.xoffset = -1.1
        self.yoffset = 2.4
        self.rotoffset = 0
        self.xscale = 164.214847759152
        self.yscale = 165.860400829302
        self.rotscale = math.pi/180
        
        # Variable for simulation
        self.port_control = 43125
        self.port_mocap = 43126
        self.host='127.0.0.1'   
        self.mocapPoll=select.poll()
        self.controlPoll=select.poll()        
        
        
        self.mocaptime = 0 # initialize mocap time
        self.pose = (0.0, 0.0, 0.0) # initialize pose
        
        nodes = self.animation.get_node_index()
        nodes = [str(node) for node in nodes]
        self.startnodecombobox.addItems(nodes)
        self.goalnodecombobox.addItems(nodes)
        
        # auxiliary variables
        
        self.mocapActive=False
        self.controlActive=False   
        self.autoControlActive=False
        
        self.connect(self, PyQt4.QtCore.SIGNAL('triggered()'), self.closeEvent)
        
    def closeEvent(self, event):
      
      self.animation.close()
    
    @pyqtSignature("bool")
    def on_enablecontrolbutton_clicked(self, checked):
        """
        Slot documentation goes here.
        """       
         
        if checked:
            if self.simulationCheckBox.isChecked():
                    try:
                        self.s_control = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket for communicating with the controller part of the C program
                    except socket.error:
                        print ('Failed to create control socket')
                        sys.exit()    
                    self.s_control.settimeout(5)
                    self.s_control.connect((self.host , self.port_control)) # connect the socket to the port for communicating with the simulated ontroller
                    self.controlPoll.register(self.s_control,select.POLLOUT) #registers the socket in the polling object for the controller
                    print "Control Socket Connected"
                    print 'Simulation active'
                    self.wlinkconnection = slink.Slink(self.s_control,self.serialPrintbrowser) #create an Slink object which uses the socket to communicate with the simulated controller
                    self.controllooptimer.start(int(1./self.controlspinbox.value()*1000.)) # start timer for periodic execution of controlupdate function
                    self.last_controlupdate = time.time()
            else:
                try:
                    self.wlinkconnection = wlink.Wlink(str(self.portlineedit.text()),self.done_callback) # create a Wlink object which communicates with the robot
                    self.controllooptimer.start(int(1./self.controlspinbox.value()*1000.)) # start timer for periodic execution of controlupdate function
                    self.last_controlupdate = time.time()
                    self.serialreadtimer.start(int(1./self.serialreadHz*1000.))
                except:
                     self.enablecontrolbutton.setChecked(False)
                     self.logbrowser.append('Could not connect to Robot! Wrong serial port?')
                     return
        else: #if the 'Control On' button is not pressed down
            self.controllooptimer.stop()  #stop the timer for the peridoic execution
            self.serialreadtimer.stop()
            self.autocontrolbutton.setChecked(False) #deactivate the 'Automatic Control On' button
            self.wlinkconnection = None
            if self.simulationCheckBox.isChecked():  #if the simlation is used
                self.controlPoll.unregister(self.s_control)
                self.s_control.close()
                print 'controller socket closed'
                
        # set several buttons according to the state of the 'Control On' button to enable or disable them
        self.controlActive=checked
        self.autocontrolbutton.setEnabled(checked)
        if self.autoControlActive==True:
            self.sendgoalbutton.setEnabled(checked)
            self.autoControlActive=False
        self.forwardbutton.setEnabled(checked)
        self.backwardbutton.setEnabled(checked)
        self.rightbutton.setEnabled(checked)
        self.leftbutton.setEnabled(checked)
        if self.mocapActive==False and self.controlActive==False:
            self.simulationCheckBox.setEnabled(True)
        else:
            self.simulationCheckBox.setEnabled(False)
        
    def controlupdate(self):
        if self.simulationCheckBox.isChecked():
            pollResponseControl = self.controlPoll.poll(0)
            if pollResponseControl[0][1]==select.POLLOUT: #checks if a connection to the controller exists
                current_time = time.time()
                control_frequency = 1./(current_time-self.last_controlupdate) #update the actual controller sampling frequency
                self.controlflabel.setText('{0:.2f} Hz'.format(control_frequency))
                self.last_controlupdate = current_time
                controlpowerstraight = self.controlpowsspinbox.value()
                controlpowerrot = self.controlpowrspinbox.value()
                # sends commands to the simulation depending on the button pressed down
                if self.forwardbutton.isDown(): 
                    serialprint_msg = self.wlinkconnection.manual_forward(controlpowerstraight)
                    if self.logbutton.isChecked():
                        self.parseNprint_SerialOutput(serialprint_msg)
                    return
                elif self.backwardbutton.isDown():
                    serialprint_msg = self.wlinkconnection.manual_backward(controlpowerstraight)
                    if self.logbutton.isChecked():
                        self.parseNprint_SerialOutput(serialprint_msg)
                    return
                elif self.rightbutton.isDown():
                    serialprint_msg = self.wlinkconnection.manual_rotateR(controlpowerrot)
                    if self.logbutton.isChecked():
                        self.parseNprint_SerialOutput(serialprint_msg)
                    return
                elif self.leftbutton.isDown():
                    serialprint_msg = self.wlinkconnection.manual_rotateL(controlpowerrot)
                    if self.logbutton.isChecked():
                        self.parseNprint_SerialOutput(serialprint_msg)
                    return
                elif self.autocontrolbutton.isChecked():
                    serialprint_msg = self.wlinkconnection.transmit_state(*self.pose)
                    if self.logbutton.isChecked():
                        self.parseNprint_SerialOutput(serialprint_msg)
                    return
                else:
                    serialprint_msg = self.wlinkconnection.manual_forward(0.)
                    if self.logbutton.isChecked():
                        self.parseNprint_SerialOutput(serialprint_msg)
        #            send control update
            else:
                self.enablecontrolbutton.setChecked(False)
                self.on_enablecontrolbutton_clicked(False)
        else:
            current_time = time.time()
            control_frequency = 1./(current_time-self.last_controlupdate) #update the actual controller sampling frequency
            self.controlflabel.setText('{0:.2f} Hz'.format(control_frequency))
            self.last_controlupdate = current_time
            controlpowerstraight = self.controlpowsspinbox.value()
            controlpowerrot = self.controlpowrspinbox.value()
            # sends commands to the robot depending on the button pressed down
            if self.forwardbutton.isDown(): 
                self.wlinkconnection.manual_forward(controlpowerstraight)
            elif self.backwardbutton.isDown():
                self.wlinkconnection.manual_backward(controlpowerstraight)
            elif self.rightbutton.isDown():
                self.wlinkconnection.manual_rotateR(controlpowerrot)
            elif self.leftbutton.isDown():
                self.wlinkconnection.manual_rotateL(controlpowerrot)
            elif self.autocontrolbutton.isChecked():
                self.wlinkconnection.transmit_state(*self.pose)
            else:
                self.wlinkconnection.manual_forward(0.)
        
    def mocapupdate(self):
        if self.simulationCheckBox.isChecked():
            pollResponseMocap= self.mocapPoll.poll(0)       
            if pollResponseMocap[0][1]==select.POLLOUT: # check the availability of the mocap connection to the simulation(C program) 
                current_time = time.time()
                mocap_frequency = 1./(current_time-self.last_mocapupdate) # get the actual samping frequency of the MoCap system
                self.mocapflabel.setText('{0:.2f} Hz'.format(mocap_frequency))
                self.last_mocapupdate = current_time
                (mocaptime, pose) = self.mocapconnection.execute() # get the current robot pose from the simulation
                if pose[0] == pose[0]:
                    self.mocaptime = mocaptime
                    self.pose = pose
                    self.xposlabel.setText('{0:.3f}'.format(self.pose[0]))
                    self.yposlabel.setText('{0:.3f}'.format(self.pose[1]))
                    self.rotposlabel.setText('{0:.3f}'.format(self.pose[2]))
                    (xs, ys, rots) = self.get_mapposition(*self.pose) # transform robot pose into pixel coordinates
                    self.animation.update(xs, ys, rots) # update the animation
                    if self.logbutton.isChecked(): # if the logging option is chosen the current pose is written into the logging file
                        self.logfile.write('%f; %.2f; %.2f; %.2f' %(self.mocaptime, self.pose[0],  self.pose[1], self.pose[2]) + '\n')
                        # update display
                        # if self.autocontrolbutton.isChecked():
                            # send state to robot
                            # print 'send current state'
            else:
                self.enablemocapbutton.setChecked(False)
                self.on_enablemocapbutton_clicked(False)
        else:
            current_time = time.time()
            mocap_frequency = 1./(current_time-self.last_mocapupdate)
            self.mocapflabel.setText('{0:.2f} Hz'.format(mocap_frequency))
            self.last_mocapupdate = current_time
            (mocaptime, pose) = self.mocapconnection.execute() # get the current robot pose from the MoCap system
            if pose[0] == pose[0]:
                self.mocaptime = mocaptime
                self.pose = pose
                self.xposlabel.setText('{0:.3f}'.format(self.pose[0]))
                self.yposlabel.setText('{0:.3f}'.format(self.pose[1]))
                self.rotposlabel.setText('{0:.3f}'.format(self.pose[2]))
                (xs, ys, rots) = self.get_mapposition(*self.pose) # transform robot pose into pixel coordinates
                self.animation.update(xs, ys, rots) # update the animation
                if self.logbutton.isChecked(): # if the logging option is chosen the current pose is written into the logging file
                    self.logfile.write('%f; %.2f; %.2f; %.2f' %(self.mocaptime, self.pose[0],  self.pose[1], self.pose[2]) + '\n')
                    # update display
                    if self.autocontrolbutton.isChecked():
                    # send state to robot
                        print 'send current state'
        return
    
    def readserial(self):
      
      messages = self.wlinkconnection.read()
      for mes in messages:
        self.serialPrintbrowser.append(mes.rstrip())
        if self.logbutton.isChecked():
          self.logfileserial.write(str(self.mocaptime) + ';' + mes.rstrip('\n') + '\n')
          
      return
      
    def done_callback(self):
#      TODO: not yet implemented
      self.logbrowser.append('Robot is done')      
      
      return
    
    
    @pyqtSignature("bool")
    def on_enablemocapbutton_clicked(self, checked):
        """
        Slot documentation goes here.
        """
        
        if checked:
            if self.simulationCheckBox.isChecked():                    
                    try:
                        self.s_mocap = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    except socket.error:
                        print ('Failed to create mocap socket')
                        sys.exit()    
                    self.s_mocap.settimeout(5)
                    self.s_mocap.connect((self.host , self.port_mocap))
                    self.mocapPoll.register(self.s_mocap,select.POLLOUT)
                    print "Mocap Socket connected"
                    self.mocapconnection = mocapSIM.MocapSIM(self.s_mocap) # set starting position to node 1
                    print 'Simulation active'
                    self.mocaplooptimer.start(int(1./self.mocapspinbox.value()*1000.)) # start timer for periodic execution of mocapupdate function
                    self.last_mocapupdate = time.time()
            else:
                try:
                    self.mocapconnection = mocap.Mocap(self.bodynumberspinbox.value())
                    self.mocaplooptimer.start(int(1./self.mocapspinbox.value()*1000.)) # start timer for periodic execution of mocapupdate function
                    self.last_mocapupdate = time.time()
                except:
                    self.enablemocapbutton.setChecked(False)
                    self.logbrowser.append('Could not connect to Mocap!')
                    return
        else:
            if self.simulationCheckBox.isChecked():  
                self.mocapPoll.unregister(self.s_mocap)
                self.s_mocap.close()
                print 'MOCAP socket closed'
            self.mocapconnection.close()
            self.mocaplooptimer.stop()
        # set several buttons according to the state of the 'Mocap On' button to enable or disable them
        self.mocapActive=checked
        self.logbutton.setEnabled(checked)
        self.usecurposbutton.setEnabled(checked)
        if self.mocapActive==False and self.controlActive==False:
            self.simulationCheckBox.setEnabled(True)
        else:
            self.simulationCheckBox.setEnabled(False)
    
    @pyqtSignature("")
    def on_loggingbutton_clicked(self):
        """
        Slot documentation goes here.
        """
       
        logfilename = QFileDialog.getSaveFileName(self, 'Open logfile', self.logfilelineedit.text())
        if logfilename != '':
            self.logfilelineedit.setText(logfilename)
    
    @pyqtSignature("bool")
    def on_autocontrolbutton_clicked(self, checked):
        """
        Slot documentation goes here.
        """

        self.sendgoalbutton.setEnabled(checked)
        self.autoControlActive=checked
        # New version
        if checked:
            #if pressed down the start and goal positions are read out and sent to the robot or the simulation
            xs = self.xstartspinbox.value()
            ys = self.ystartspinbox.value()
            xg = self.xgoalspinbox.value()
            yg = self.ygoalspinbox.value()
            self.logbrowser.append('Send robot from x:{0:.2f}, y:{1:.2f} to x:{2:.2f}, y:{3:.2f}'.format(xs,ys,xg,yg))
            serialprint_msg = self.wlinkconnection.transmit_startgoal(xs,ys,xg,yg)
            if self.logbutton.isChecked():
                self.parseNprint_SerialOutput(serialprint_msg)
        
        
    def get_mapposition(self, realx, realy, realrot):
        # converts a position on the displayed map into a position in the mocap frame
        mapx = (realx-self.xoffset)*self.xscale
        mapy = (realy-self.yoffset)*self.yscale*-1.
        maprot = (-1*realrot-self.rotoffset)*self.rotscale
        return int(mapx), int(mapy), maprot
        
    def get_realposition(self, mapx, mapy):
        # converts a position in the mocap frame  into a position on the displayed map
        realx = mapx/self.xscale + self.xoffset
        realy = -1*mapy/self.yscale + self.yoffset
        return (realx, realy)
    
    @pyqtSignature("bool")
    def on_logbutton_clicked(self, checked):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        if checked:
            # open file for logging
            try:
                self.logbrowser.append('start logging')
                name=self.logfilelineedit.text()
                self.logfile=open(name, 'a')
                i=0
                for c in name:
                    if c!='.':
                        i+=1
                    else:
                        break
                filename = name[:i] + '_serial' + name[i:]
                self.logfileserial = open(filename,'a')
                self.logfile.write('t; x; y; theta\n')
                self.logfileserial.write('Time; Serial.print output \n')
            except:
                self.logbrowser.append('Could not open file!')
                self.logbutton.setChecked(False)
        else:
            # close file
            self.logbrowser.append('stop logging')
            self.logfile.close()
            self.logfileserial.close()
    
    @pyqtSignature("")
    def on_usecurposbutton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.xstartspinbox.setValue(self.pose[0])
        self.ystartspinbox.setValue(self.pose[1])
    
    @pyqtSignature("QString")
    def on_startnodecombobox_activated(self, node):
        """
        Slot documentation goes here.
        """
        pos = self.get_realposition(*self.animation.get_node_position(int(node)))
        self.xstartspinbox.setValue(pos[0])
        self.ystartspinbox.setValue(pos[1])
        print self.animation.get_node_position(int(node))
        
    
    @pyqtSignature("QString")
    def on_goalnodecombobox_activated(self, node):
        """
        Slot documentation goes here.
        """
        pos = self.get_realposition(*self.animation.get_node_position(int(node)))
        self.xgoalspinbox.setValue(pos[0])
        self.ygoalspinbox.setValue(pos[1])
    
    @pyqtSignature("")
    def on_sendgoalbutton_clicked(self):
        """
        Slot documentation goes here.
        """
        xs = self.xstartspinbox.value()
        ys = self.ystartspinbox.value()
        xg = self.xgoalspinbox.value()
        yg = self.ygoalspinbox.value()
        self.logbrowser.append('Send robot from x:{0:.2f}, y:{1:.2f} to x:{2:.2f}, y:{3:.2f}'.format(xs,ys,xg,yg))
        serialprint_msg = self.wlinkconnection.transmit_startgoal(xs,ys,xg,yg)
        if self.logbutton.isChecked():
            self.parseNprint_SerialOutput(serialprint_msg)
            
         
                