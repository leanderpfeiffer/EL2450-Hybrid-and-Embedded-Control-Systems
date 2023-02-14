# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial

In this example we draw 6 lines using
different pen styles.

author: Jan Bodnar
website: zetcode.com
last edited: September 2011
"""

import sys
from PyQt4 import QtGui, QtCore
import math



class corridor_animation(QtGui.QMainWindow):


    def __init__(self):
        super(corridor_animation, self).__init__()
        self.initUI()


    def initUI(self):

        self.size = width, height = 800,800

        self.setGeometry(300, 300, *self.size)
        self.setWindowTitle('Pen styles')
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(p)
        self.show()

        # position in a x,y grid (zero is upper left, x is horizontal, y is vertical)
        self.nodes = {1:(1,1),2:(3,1),3:(5,1),4:(1,3),5:(3,3),6:(5,3),7:(1,5),8:(3,5),9:(5,5)}
        # edges connecting the nodes
        self.edges = ((1,2),(2,3),(4,5),(5, 6),(7,8),(8,9), (1, 4), (2, 5), (3, 6), (4, 7,), (5, 8), (6, 9))

        self.path = (1,2,3, 6, 5, 8)

        self.size = width, height = 800,800
        self.cw = 60 # corridorwidth
        self.pw = 3 # pathwidth
        self.grid_size = 2*self.cw
        # self.myfont = pygame.font.SysFont("monospace", 15)

        self.x = 50
        self.y = 50
        self.rot = 0

        self.nodes_pos = {node:(gridpos[0]*self.grid_size,gridpos[1]*self.grid_size) for node,gridpos in self.nodes.iteritems()}

        self.renderfrequency = 25;
        self.rendertimer = QtCore.QTimer()
        self.rendertimer.timeout.connect(self.repaint)
        self.rendertimer.start(int(1./self.renderfrequency*1000.))

#        self.draw_robot(1, 1, 0)


    def draw_background(self, qp):

        pen = QtGui.QPen(QtCore.Qt.white, self.cw, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        for edge in self.edges:
          qp.drawLine(self.nodes_pos[edge[0]][0],self.nodes_pos[edge[0]][1],self.nodes_pos[edge[1]][0],self.nodes_pos[edge[1]][1])

        qp.setPen(QtCore.Qt.black)
        qp.setFont(QtGui.QFont('Decorative', 10))
        for node,pos in self.nodes_pos.iteritems():
          qp.drawText(pos[0],pos[1], str(node))

    def draw_robot(self, x, y, rot, qp):

        self.draw_background(qp)
        x = int(x)
        y = int(y)

        qp.setBrush(QtGui.QBrush(QtCore.Qt.yellow))
        qp.drawEllipse(QtCore.QPoint(x,y),self.cw/3,self.cw/3)
        qp.setPen(QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine))
        qp.drawLine(x,y,x+self.cw/3*math.cos(rot),y+self.cw/3*math.sin(rot))
        return

    def update(self,x,y,rot):
        self.x = x
        self.y = y
        self.rot = rot

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_robot(self.x,self.y,self.rot,qp)
        qp.end()


    def get_node_position(self, node):
        return self.nodes_pos[node]

    def get_node_index(self):
        return [node for node in self.nodes]


#def main():
#
#    app = QtGui.QApplication(sys.argv)
#    ex = corridor_animation()
#    sys.exit(app.exec_())
#
#
#if __name__ == '__main__':
#    main()
