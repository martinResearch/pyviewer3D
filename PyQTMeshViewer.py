# inpired by
# PyQT + OpenGL :
#   http://www.siafoo.net/snippet/316
#   http://pyqglviewer.gforge.inria.fr/wiki/doku.php?id=examples # could not install it....
# QT file loader
# collada example print_collada_info.py

import sys
from PyQt4 import QtGui
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4 import QtGui
from PyQt4.QtOpenGL import *
from PyGLWidget import PyGLWidget
import collada #from  https://github.com/pycollada/pycollada
import meshconvert # from https://code.google.com/p/meshconvert/
import math
import os



class MeshWidget(PyGLWidget):

    def __init__(self, parent):
        PyGLWidget.__init__(self, parent)
        self.col=[]

    def loadPoint(points)
        self.points=points

    def paintGL(self):
        PyGLWidget.paintGL(self)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        scale=0.01

       
        #glEnableClientState(GL_NORMAL_ARRAY)
        #glNormalPointerf( prim.normal)#http://www.opengl.org/discussion_boards/ubbthreads.php?ubb=showflat&Number=264532
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointerf( prim.vertex*scale)

        glDrawElementsui(GL_TRIANGLES,prim.vertex_index)

##                        glBegin(GL_TRIANGLES)                 # Start drawing a polygon
##                        for tri  in prim.triangles():
##
##
##                            glNormal3f(tri.normals[0,0],tri.normals[0,1],tri.normals[0,2])
##                            glVertex3f(tri.vertices[0,0]*scale,tri.vertices[0,1]*scale,tri.vertices[0,2]*scale)
##
##                            glNormal3f(tri.normals[1,0],tri.normals[1,1],tri.normals[1,2])
##                            glVertex3f(tri.vertices[1,0]*scale,tri.vertices[1,1]*scale,tri.vertices[1,2]*scale)
##
##                            glNormal3f(tri.normals[2,0],tri.normals[2,1],tri.normals[2,2])
##                            glVertex3f(tri.vertices[2,0]*scale,tri.vertices[2,1]*scale,tri.vertices[2,2]*scale)
##
##                        glEnd()
        glFlush()





class Example(QtGui.QMainWindow):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):

        self.glWidget = ColladaWidget(self)
        self.setCentralWidget(self.glWidget)
        self.statusBar()

        openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('File dialog')
        self.show()

    def showDialog(self):

        fname = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file',       os.getcwd()))
        inputFormat=meshconvert.getFormat(fname,"garbage")
        inputModule =  __import__("meshconvert."+inputFormat, globals(),  locals(), [""])
        file =open(fname ,'r')
        r=inputModule.reader(file)
        
        vertices=[]
        for t in r.readNode():
            vertices.append([t.x,t.y,t.z])
        # creat numpy arrays
        # vertices
        # normals
        # faces
        
        #self.glWidget.loadCollada(fname)




def main():

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
