# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 15:54:56 2015

@author: David
"""

#parser of response message for a command type of message
import sys      #for exit
import struct
import math

class MocapSIM(object):

    def __init__(self, socket):

        # self.id = 'mocap'
        # #self.bodynr = bodynr
        # self.socket = socket
        # self.starttime = 0
        # self.pose = position
        # self.time = 0.0

        self.id = 'mocap'
        #self.bodynr = bodynr
        self.socket = socket
        pose_cm, self.starttime = self.bodyinfo()
        self.pose = [x/100 for x in pose_cm[0:2]]
        self.pose.append(pose_cm[2])
        self.time = 0.0

    def execute(self):

        # UNCOMMENT IF ROBOT IS SIMULATED IN MOCAPSIM
        control, mocaptime = self.bodyinfo()
        sample_time=1.0/60.0
        x = self.pose[0] + 0.5*0.001*(control[0]+control[1])*math.cos(self.pose[2]*math.pi/180)*sample_time
        y = self.pose[1] + 0.5*0.001*(control[0]+control[1])*math.sin(self.pose[2]*math.pi/180)*sample_time
        theta = self.pose[2] + (0.001/0.005)*(control[1]-control[0])*sample_time
        if theta>=180:
           theta=theta-360
        elif theta<-180:
           theta=theta+360

        self.pose = [x,y,theta]

        pose_cm, mocaptime = self.bodyinfo()
        self.pose = [x/100 for x in pose_cm[0:2]] # convert the cm values of the simulation into m values
        self.pose.append(pose_cm[2]) # append theta
        #print 'mocaptime: ', mocaptime
        #print 'self.time: ', self.time ', self.starttime', self.starttime
        self.time = mocaptime - self.starttime

        # time updated with the mocap time
        return (self.time, self.pose)

    def close(self):
        #self.socket.close()
        print "Mocap socket closed"

#    def build_packet(self,data,type):
#        if sys.version_info > (2, 8):
#            data_bytes = bytes(data,'UTF-8')
#        else:
#            data_bytes = bytearray(data,'UTF-8')
#        data_len = len(data_bytes)
#        packet_size = data_len + 9 #message size plus 8B of header and 1B of \x00 trailer
#        header_size = struct.pack('>l',packet_size)
#        header_type = struct.pack('>l',type)
#        msg_to_send = header_size + header_type + data_bytes + b'\x00'
#        return msg_to_send

#    def ask_for_6DOFinfo(self,socket):
#        str_to_send = 'GetCurrentFrame 6DEuler'
#        msg = self.build_packet(str_to_send,1)
#        socket.sendall(msg)

#    def find_bodies(self, socket, printinfo=True):
#        self.ask_for_6DOFinfo(socket)
#        z, t, b, ts = self.parser_comm(socket)
#        valid = []
#        print ('---Valid bodies in the workspace:---')
#        for ii in range(len(b)): #foreach body in the configuration file, check if the body is in the workspace
#            if not math.isnan(sum(b[ii])):
#                valid.append(ii+1)
#                if printinfo:
#                    print('body nr. '  + str(ii+1) +  ' is valid\nx= ' + str(b[ii][0]) + '\ny= ' + str(b[ii][1]) + '\n')
#        return valid

    def bodyinfo(self):
        state_msg=":state?;"
        b = state_msg.encode("ascii") #Format it correctly and...
        self.socket.send(b)
        msgstr=self.socket.recv(128)
        msg=b""
        c=0
        for a in msgstr:
            if c==1 and a!=b";":
                msg+=a
            elif c==1 and a==b";":
                break
            if c==0:
                if a==b":":
                    c=1
        try:
            #junk, left, right, timestamp = msg.decode("ascii").split(" ")
            junk, x, y, theta, timestamp = msg.decode("ascii").split(" ")
        except:
            print "The message is: "+msgstr


        #dof = float(left), float(right)
        dof = float(x), float(y), float(theta)
        return dof, float(timestamp)

#    def parser_comm(self, socket):
#        msg_size_bytes = socket.recv(4) #receive the size of the package
#        msg_size = struct.unpack('>l', msg_size_bytes)[0] #get the decimal message size
#        msg_type_bytes = socket.recv(4) #receive the type of message
#        msg_type_code = struct.unpack('>l', msg_type_bytes)[0] #get the decimal message size
#        if msg_type_code == 0:
#            msg_type = 'Error'
#        elif msg_type_code == 1:
#            msg_type = 'Command'
#        elif msg_type_code == 2:
#            msg_type = 'XML'
#        elif msg_type_code == 3:
#            msg_type = 'Data'
#            # parse the rest of the header
#            header_timestamp = socket.recv(8)
#            timestamp = struct.unpack('>q', header_timestamp)[0]
#            header_framenumber = socket.recv(4)
#            #print(struct.unpack('>l', header_framenumber)[0] )
#            header_componentcount = socket.recv(4)
#            nr_componentcount = struct.unpack('>l', header_componentcount)[0]
#            for ii in range(nr_componentcount): #only one iteration if you request the current frame
#                component_size = socket.recv(4)
#                nr_comp_size = struct.unpack('>l', component_size)[0]
#                component_type = socket.recv(4)
#                nr_comp_type = struct.unpack('>l', component_type)[0]
#                if nr_comp_type != 6:
#                    raise Exception('requested data type not manageable by the parser')
#                body_count = struct.unpack('>l',socket.recv(4))[0]
#                useless_info = socket.recv(4)
#                bodies = [0]*body_count
#                for jj in range(body_count):
#                    x = struct.unpack('>f',socket.recv(4))[0]
#                    y = struct.unpack('>f',socket.recv(4))[0]
#                    z = struct.unpack('>f',socket.recv(4))[0]
#                    a1 = struct.unpack('>f',socket.recv(4))[0]
#                    a2 = struct.unpack('>f',socket.recv(4))[0]
#                    a3 = struct.unpack('>f',socket.recv(4))[0]
#                    bodies[jj] = [x, y, z, a1, a2, a3]
#            return msg_size, msg_type, bodies, timestamp
#        elif msg_type_code == 4:
#            msg_type = 'No more Data'
#            return msg_size, msg_type, None
#        else:
#            raise Exception('unexpexted type of message, see protocol documentation')
#        qtm_message_bytes = socket.recv(msg_size-8) #receive the message (size+type are 8B)
#        qtm_message = qtm_message_bytes.decode("UTF-8")
#        return msg_size, msg_type, qtm_message

#if __name__ == "__main__":
#    sk = create_connection()
#    find_bodies(sk)
