#parser of response message for a command type of message
import socket   #for sockets
import sys      #for exit
import struct
import math

class Mocap(object):
    
    def __init__(self, bodynr):
        self.id = 'mocap'
        self.bodynr = bodynr
        self.socket = self.create_connection()
        pose_mm, self.starttime = self.bodyinfo(self.socket, self.bodynr, 'xya')
        self.pose = [x/1000 for x in pose_mm[0:2]]
        self.pose.append(pose_mm[2])
        self.time = 0.0

    # def publish(self, ros):
    #     ros.pool['cur_pose'] = self.pose
    #     ros.pool['time'] = self.time
    #     print '*mocap* publish [cur_pose] (%.2f, %.2f, %.2f) at time %.2f' %(self.pose[0], self.pose[1], self.pose[2], self.time)
    #     ros.distribute()

    # def execute(self, ros):
    #     pose_mm, mocaptime = self.bodyinfo(self.socket, self.bodynr, 'xya')
    #     self.pose = [x/1000 for x in pose_mm[0:2]]
    #     self.pose.append(pose_mm[2])
    #     #print 'mocaptime: ', mocaptime
    #     #print 'self.time: ', self.time ', self.starttime', self.starttime
    #     self.time = mocaptime - self.starttime
    #     # time updated with the mocap time
    #     self.publish(ros)

    def execute(self):
        pose_mm, mocaptime = self.bodyinfo(self.socket, self.bodynr, 'xya')
        self.pose = [x/1000 for x in pose_mm[0:2]]
        self.pose.append(pose_mm[2])
        #print 'mocaptime: ', mocaptime
        #print 'self.time: ', self.time ', self.starttime', self.starttime
        self.time = mocaptime - self.starttime
        # time updated with the mocap time
        return (self.time, self.pose)

    def close(self):
        self.socket.close()

    def create_connection(self,printinfo=True):
        #create socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print ('Failed to create socket')
            sys.exit()
        if printinfo:
            print ('\nSocket Created \n')

        #IP and PORT of the Qtm PC
        host = '192.168.1.146';
        port = 22224;

        #create a socket connection
        s.settimeout(5)
        s.connect((host , port))
        if printinfo:
            print ('Socket Connected on host ' + host + ' port ' + str(port) + '\n')

        #Parse the WELCOME MESSAGE (always 35 Bytes)
        w_size,w_type,w_mess = self.parser_comm(s);
        if printinfo:
            print('---Qualysis message:---')
            print(w_mess + '\n')

        # set the communication protocol version to 1.11
        str_to_send = 'Version 1.11'
        msg = self.build_packet(str_to_send,1);
        s.sendall(msg)
        # Parse the VERSION MESSAGE
        v_size,v_type,v_mess = self.parser_comm(s)
        if printinfo:
            print('---Qualysis message:---')
            print(v_mess + '\n')
        return s

    def build_packet(self,data,type):
        if sys.version_info > (2, 8):
            data_bytes = bytes(data,'UTF-8')
        else:
            data_bytes = bytearray(data,'UTF-8')
        data_len = len(data_bytes)
        packet_size = data_len + 9 #message size plus 8B of header and 1B of \x00 trailer
        header_size = struct.pack('>l',packet_size) #formats packet_size according to the format '>l', which means big endian and long
        header_type = struct.pack('>l',type) #formats type according to the format '>l', which means big endian and long
        msg_to_send = header_size + header_type + data_bytes + b'\x00'
        return msg_to_send

    def ask_for_6DOFinfo(self,socket):
        str_to_send = 'GetCurrentFrame 6DEuler'
        msg = self.build_packet(str_to_send,1)
        socket.sendall(msg)

    def find_bodies(self, socket, printinfo=True):
        self.ask_for_6DOFinfo(socket)
        z, t, b, ts = self.parser_comm(socket)
        valid = []
        print ('---Valid bodies in the workspace:---')
        for ii in range(len(b)): #for each body in the configuration file, check if the body is in the workspace
            if not math.isnan(sum(b[ii])):
                valid.append(ii+1)
                if printinfo:
                    print('body nr. '  + str(ii+1) +  ' is valid\nx= ' + str(b[ii][0]) + '\ny= ' + str(b[ii][1]) + '\n')
        return valid

    def bodyinfo(self,socket,bodynr,datatype='xy'):
        self.ask_for_6DOFinfo(socket)
        z, t, bodies, timestamp = self.parser_comm(socket)
        mybody = bodies[bodynr-1]
        x = mybody[0]
        y = mybody[1]
        z = mybody[2]
        a1 = mybody[3]
        a2 = mybody[4]
        a3 = mybody[5]
        if datatype == 'xy':
            dof = x, y
        elif datatype == 'xya':
            dof = x, y, a3
        elif datatype == 'xyz':
            dof =  x, y, z
        elif datatype == 'xyza':
            dof = x, y, z, a1, a2, a3
        else:
            raise Exception('Invalid data type request')
        # ldof = list(dof)
        # ldof.append(timestamp)
        # dof = tuple(ldof)
        return dof, timestamp

    def parser_comm(self, socket):
        msg_size_bytes = socket.recv(4) #receive the message size...
        msg_size = struct.unpack('>l', msg_size_bytes)[0] #... and format it to a value which is usable
        msg_type_bytes = socket.recv(4) #receive the type of message...
        msg_type_code = struct.unpack('>l', msg_type_bytes)[0] #...and format it to a value which is usable
        if msg_type_code == 0:
            msg_type = 'Error'
        elif msg_type_code == 1:
            msg_type = 'Command'
        elif msg_type_code == 2:
            msg_type = 'XML'
        elif msg_type_code == 3:
            msg_type = 'Data'
            # parse the rest of the header
            header_timestamp = socket.recv(8)
            timestamp = struct.unpack('>q', header_timestamp)[0]
            header_framenumber = socket.recv(4)
            #print(struct.unpack('>l', header_framenumber)[0] )
            header_componentcount = socket.recv(4)
            nr_componentcount = struct.unpack('>l', header_componentcount)[0]
            for ii in range(nr_componentcount): #only one iteration if you request the current frame
                component_size = socket.recv(4)
                nr_comp_size = struct.unpack('>l', component_size)[0]
                component_type = socket.recv(4)
                nr_comp_type = struct.unpack('>l', component_type)[0]
                if nr_comp_type != 6:
                    raise Exception('requested data type not manageable by the parser')
                body_count = struct.unpack('>l',socket.recv(4))[0]
                useless_info = socket.recv(4)
                bodies = [0]*body_count
                for jj in range(body_count):
                    x = struct.unpack('>f',socket.recv(4))[0]
                    y = struct.unpack('>f',socket.recv(4))[0]
                    z = struct.unpack('>f',socket.recv(4))[0]
                    a1 = struct.unpack('>f',socket.recv(4))[0]
                    a2 = struct.unpack('>f',socket.recv(4))[0]
                    a3 = struct.unpack('>f',socket.recv(4))[0]
                    bodies[jj] = [x, y, z, a1, a2, a3]
            return msg_size, msg_type, bodies, timestamp
        elif msg_type_code == 4:
            msg_type = 'No more Data'
            return msg_size, msg_type, None
        else:
            raise Exception('unexpexted type of message, see protocol documentation')
        qtm_message_bytes = socket.recv(msg_size-8) #receive the message (size+type are 8B)
        qtm_message = qtm_message_bytes.decode("UTF-8")
        return msg_size, msg_type, qtm_message

if __name__ == "__main__":
    sk = create_connection()
    find_bodies(sk)
