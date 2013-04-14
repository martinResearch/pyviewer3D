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
from PyQt4.QtOpenGL import *
from PyGLWidget import PyGLWidget
#import collada #from  https://github.com/pycollada/pycollada
import meshconvert # from https://code.google.com/p/meshconvert/
import math
import os
import numpy
import OpenGL.arrays.vbo as glvbo

def normalize_v3(arr):
    # from https://sites.google.com/site/dlampetest/python/calculating-normals-of-a-triangle-mesh-using-numpy
    ''' Normalize a numpy array of 3 component vectors shape=(n,3) '''
    lens = numpy.sqrt( arr[:,0]**2 + arr[:,1]**2 + arr[:,2]**2 )
    arr[:,0] /= lens
    arr[:,1] /= lens
    arr[:,2] /= lens                
    return arr


def computeFaceNormals(faces,vertices):
    # from https://sites.google.com/site/dlampetest/python/calculating-normals-of-a-triangle-mesh-using-numpy   
    #Create an indexed view into the vertex array using the array of three indices for triangles
    tris = vertices[faces]
    #Calculate the normal for all the triangles, by taking the cross product of the vectors v1-v0, and v2-v0 in each triangle             
    n = numpy.cross( tris[::,1 ] - tris[::,0]  , tris[::,2 ] - tris[::,0] )
    # n is now an array of normals per triangle. The length of each normal is dependent the vertices, 
    # we need to normalize these, so that our next step weights each normal equally.
    normalize_v3(n)
    return n

          
def computeVertexNormals(faces,vertices):         
    n=computeFaceNormals(faces,vertices)
    # now we have a normalized array of normals, one per triangle, i.e., per triangle normals.
    # But instead of one per triangle (i.e., flat shading), we add to each vertex in that triangle, 
    # the triangles' normal. Multiple triangles would then contribute to every vertex, so we need to normalize again afterwards.
    # The cool part, we can actually add the normals through an indexed view of our (zeroed) per vertex normal array    
    #Create a zeroed array with the same type and shape as our vertices i.e., per vertex normal
    norm = numpy.zeros( vertices.shape, dtype=vertices.dtype )        
    norm[ faces[:,0] ] += n
    norm[ faces[:,1] ] += n
    norm[ faces[:,2] ] += n
    normalize_v3(norm)
    return norm 

class ColladaWidget(PyGLWidget):

    def __init__(self, parent):
        PyGLWidget.__init__(self, parent)
        self.col=[]

    def loadCollada(self,fname):
        self.col = collada.Collada(fname, ignore=[collada.DaeUnsupportedError,
                                            collada.DaeBrokenRefError])


    def paintGL(self):
        PyGLWidget.paintGL(self)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        scale=0.01

        if self.col:
            if self.col.scene is not None:
                for geom in self.col.scene.objects('geometry'):
                    for prim in geom.primitives():
                        prim.generateNormals() # regenerate normals to make sure there is only one normal per vertex (glDrawElementsui can take only on array of indices), this assume the surface to be smooth

                        glEnableClientState(GL_NORMAL_ARRAY)
                        glNormalPointerf( prim.normal)#http://www.opengl.org/discussion_boards/ubbthreads.php?ubb=showflat&Number=264532
                        glEnableClientState(GL_VERTEX_ARRAY)
                        glVertexPointerf( prim.vertex*scale)

                        glDrawElementsui(GL_TRIANGLES,prim.vertex_index)
        glFlush()


class MeshWidget(PyGLWidget):

    def __init__(self, parent):
        PyGLWidget.__init__(self, parent)
        self.col=[]
        self.points= []
        self.pointsColors=[]
        self.faces=[]
        parent.setCentralWidget(self)

    def plotPoints(self,points,vertexColors=[],faces=[],normals=[],faceColors=[]):
        self.points=numpy.array(points,dtype=numpy.float32)
        self.pointsColors=numpy.array(vertexColors,dtype=numpy.float32)
        self.faces=numpy.array(faces,dtype=numpy.uint32)
        self.faceColors=[]
        if len(faceColors)>0:
            
            #self.faceColors=numpy.array(faceColors,dtype=numpy.float32)            
            self.pointsColors=numpy.zeros((self.points.shape[0],3),dtype=numpy.float32)            
            for i in range(3):
                self.pointsColors[self.faces[:,i],:]=faceColors # warning this assume that faces do not share vertices
        assert(max(self.faces.flatten())<self.points.shape[0])
        if faces!=[]: 
            if normals==[]:
                self.normals=computeVertexNormals(self.faces,self.points)
            else:        
                self.normals=normals
        self.scale=1
        #self.faces=numpy.array([[1,2,3],[3,4,5]],dtype=numpy.int32)
        # create a Vertex Buffer Object with the specified data
        self.vbo = glvbo.VBO(self.points)    # from # http://cyrille.rossant.net/blog/page/3/   
        

              
            
    def paintGL(self):
        PyGLWidget.paintGL(self)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glShadeModel(GL_SMOOTH)
        if len(self.faces)>0:
            glEnable(GL_LIGHT0)
            glEnable(GL_LIGHTING)
            if len(self.pointsColors)>0:
                glColorMaterial ( GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
                glEnable ( GL_COLOR_MATERIAL )            
        

       
        #glEnableClientState(GL_NORMAL_ARRAY)
        #glNormalPointerf( prim.normal)#http://www.opengl.org/discussion_boards/ubbthreads.php?ubb=showflat&Number=264532
      
        if len(self.points)>0:
            if len(self.faces)>0:  
                #draw a triangulated mesh
                #glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                glEnableClientState(GL_NORMAL_ARRAY)
                glNormalPointerf( self.normals)
                if len(self.pointsColors)>0:
                    glEnableClientState(GL_COLOR_ARRAY)                 
                glEnableClientState(GL_VERTEX_ARRAY)#tell OpenGL that the VBO contains an array of vertices
                glVertexPointerf( self.points*self.scale)
                if len(self.pointsColors)>0:                    
                    glColorPointerf(self.pointsColors)                       
                if len(self.faceColors)>0:
                    # I am strugling to display flat color triangles
                    # http://stackoverflow.com/questions/6056679/gldrawelements-and-flat-shading
                    #glShadeModel(GL_FLAT);
                    #glEnableClientState(GL_COLOR_ARRAY)
                    #glColorPointerf( self.faceColors)    
                    #glGenBuffer(1,self.faceColors)
                    #glBindBuffer(GL_ARRAY_BUFFER,self.faceColors);
                    #tmp=numpy.array(range(self.faces.shape[0]))*numpy.ones((1,3))
                    #glVertexAttribPointer(1, tmp)
                    #glEnableVertexAttribArray(1)
                    pass
                                                  
                    
                    
                glDrawElementsui(GL_TRIANGLES,self.faces)
                glDisableClientState(GL_COLOR_ARRAY);
                glDisableClientState(GL_VERTEX_ARRAY);                
            else: 
                # draw point cloud
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
              
        glFlush()
  
        
    def openMesh(self,fname):
        inputFormat=meshconvert.getFormat(fname,"garbage")
        inputModule =  __import__("meshconvert."+inputFormat, globals(),  locals(), [""])
        file =open(fname ,'r')
        r=inputModule.reader(file)
        
        vertices=[]
        vertexColors=[]
        for t in r.readNode():
            vertices.append([float(t.x),float(t.y),float(t.z)])
            vertexColors.append([float(x)/255 for x in t.color])
        
        faces=[]
        for t in r.readElementIndexed():
                faces.append([int(i) for i in t.list])
        faces= numpy.array(faces,dtype=numpy.int32)   
        vertices=numpy.array(vertices,dtype=numpy.float32)         
       
        self.plotPoints(vertices,vertexColors=vertexColors,faces=faces)    
        





class SimpleMeshViewerUI(QtGui.QMainWindow):

    def __init__(self):
        super(SimpleMeshViewerUI, self).__init__()

        self.initUI()

    def initUI(self):

        self.glWidget = MeshWidget(self)
     
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
        self.glWidget.openMesh(fname)




def main():

    app = QtGui.QApplication(sys.argv)
    ex = SimpleMeshViewerUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
