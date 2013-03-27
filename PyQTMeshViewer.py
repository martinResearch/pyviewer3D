# inpired by
# PyQT + OpenGL :
#   http://www.siafoo.net/snippet/316
#   http://pyqglviewer.gforge.inria.fr/wiki/doku.php?id=examples # could not install it....
# QT file loader
# collada example print_collada_info.py 
# could have a look at http://rossant.github.com/galry/ that seem to be able to plot multi miliions of points in python

import sys
from PyQt4 import QtGui
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4 import QtGui
from PyQt4.QtOpenGL import *
from PyGLWidget import PyGLWidget
#import collada #from  https://github.com/pycollada/pycollada
import meshconvert # from https://code.google.com/p/meshconvert/
import math
import os
import numpy
import OpenGL.arrays.vbo as glvbo


class MeshWidget(PyGLWidget):

    def __init__(self, parent):
        PyGLWidget.__init__(self, parent)
        self.col=[]
        self.points= []
        self.pointsColors=[]

    def plotPoints(self,points,vertexColors=[]):
        self.points=numpy.array(points,dtype=numpy.float32)
        self.pointsColors=numpy.array(vertexColors,dtype=numpy.float32)
        self.scale=1
        #self.faces=numpy.array([[1,2,3],[3,4,5]],dtype=numpy.int32)
        # create a Vertex Buffer Object with the specified data
        self.vbo = glvbo.VBO(self.points)    # from # http://cyrille.rossant.net/blog/page/3/    
        
    def paintGL(self):
        PyGLWidget.paintGL(self)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glShadeModel(GL_SMOOTH)
        #glEnable(GL_LIGHT0)
        #glEnable(GL_LIGHTING)
        

       
        #glEnableClientState(GL_NORMAL_ARRAY)
        #glNormalPointerf( prim.normal)#http://www.opengl.org/discussion_boards/ubbthreads.php?ubb=showflat&Number=264532
      
        if len(self.points)>0:
                         
            glColor( 0.95, 0.207, 0.031 )
            glPointSize( 6.0 )
            glEnable( GL_POINT_SMOOTH )
            glEnableClientState(GL_COLOR_ARRAY)
                  
            glEnableClientState(GL_VERTEX_ARRAY)#tell OpenGL that the VBO contains an array of vertices
            glVertexPointerf( self.points*self.scale)
            glColorPointerf(self.pointsColors)     
            #self.vbo.bind() # bind the VBO 
            #glVertexPointer(3, GL_FLOAT, 0, self.vbo) # these vertices contain 3 single precision coordinates
            glDrawArrays(GL_POINTS, 0, self.points.shape[0])   # draw "count" points from the VBO
          
            #glDrawElementsui(GL_POINTS,self.points*self.scale)
            #glDrawElementsui(GL_TRIANGLES,self.faces)

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

        self.glWidget = MeshWidget(self)
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
        vertexColors=[]
        for t in r.readNode():
            vertices.append([float(t.x),float(t.y),float(t.z)])
            vertexColors.append([float(x)/255 for x in t.color])
            
        self.glWidget.plotPoints(vertices,vertexColors=vertexColors)    
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
