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


import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class Point():
    def __init__(self,coord,color=[]):
        self.coord=coord
        self.color=color



class vtkMeshWidget ():
    def __init__(self,MainWindow):

        self.centralWidget = QtGui.QWidget(MainWindow)
        self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)
        self.gridlayout = QtGui.QGridLayout(self.centralWidget)
        self.gridlayout.setMargin(0)
        self.gridlayout.addWidget(self.vtkWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)
        renWin= self.vtkWidget.GetRenderWindow()
        self.renWin=renWin
        self.ren = vtk.vtkRenderer()
        self.renWin.AddRenderer(self.ren)
        self.iren = self.renWin.GetInteractor()
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.iren.AddObserver("KeyPressEvent", self.Keypress)
        self.iren .Initialize()


    def Keypress(self):
        pass







    def camera_actor( self,camera):
        corners = camera.image_corners()
        vtk_points = vtk.vtkPoints()
        for p in corners:
            print p
            vtk_points.InsertNextPoint(p[0],p[1],p[2])

        p= camera.optical_center()
        vtk_points.InsertNextPoint(p[0],p[1],p[2])


        # Create a cell array to store the lines in and add the lines to it


        polygons = vtk.vtkCellArray()
        polygon = vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(4) #make a quad
        polygon.GetPointIds().SetId(0, 0);
        polygon.GetPointIds().SetId(1, 1);
        polygon.GetPointIds().SetId(2, 2);
        polygon.GetPointIds().SetId(3, 3);
        polygons.InsertNextCell(polygon);
        lines = vtk.vtkCellArray()
        for i in range(4):
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, i);
            line.GetPointIds().SetId(1, 4);
            lines.InsertNextCell(line);
        for i in range(4):
            line.GetPointIds().SetId(0, i);
            line.GetPointIds().SetId(1, mod(i+1,4));
            lines.InsertNextCell(line);


        # this these notations are heavy , shoulf be something simple like polygon = vtk.vtkPolygon([0,1,4]) !!!


        # Create a polydata to store everything in
        quad = vtk.vtkPolyData()
        quad.SetPoints(vtk_points);
        quad.SetPolys(polygons);
        # Add the lines to the dataset
        frustrum = vtk.vtkPolyData()
        frustrum. SetPoints(vtk_points);
        frustrum .SetLines(lines)

        # apd = vtk.vtkAppendPolyData()
        #apd.addInput()

        textureCoordinates = vtk.vtkFloatArray()
        textureCoordinates.SetNumberOfComponents(2)
        textureCoordinates.SetName("TextureCoordinates")
        textureCoordinates.InsertNextTuple2(1.0, 1.0)
        textureCoordinates.InsertNextTuple2(0.0, 1.0)
        textureCoordinates.InsertNextTuple2(0.0, 0.0)
        textureCoordinates.InsertNextTuple2(1.0, 0.0)

        quad.GetPointData().SetTCoords(textureCoordinates)

        print camera.image
        vtk_JPEGreader = vtk.vtkJPEGReader()
        vtk_JPEGreader.SetFileName( camera.image )
        vtk_JPEGreader.Update()

        flipFilter = vtk.vtkImageFlip()
        flipFilter.SetInputConnection(vtk_JPEGreader.GetOutputPort())
        flipFilter.Update()

        texture = vtk.vtkTexture()
        texture.SetInput(flipFilter.GetOutput())


        ass=vtk.vtkAssembly()





        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(  frustrum)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(1)
        actor.GetProperty().SetColor(0.5,0.5,0.5)# set the line color
        ass.AddPart(actor)


        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(quad)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.SetTexture(texture)
        actor.GetProperty().SetOpacity( 0.5 );
        ass.AddPart(actor)






        return ass






    def vtk_point_cloud(self,points):

        vtk_points = vtk.vtkPoints()
        vtk_verts = vtk.vtkCellArray()
        vtk_colors = vtk.vtkUnsignedCharArray()
        vtk_colors.SetNumberOfComponents(3)
        vtk_colors.SetName( "Colors")
        cell = 0

        box=numpy.zeros(shape=(3,2),dtype=float)
        box[:,0]=numpy.inf
        box[:,1]=-numpy.inf


        for point in points:
            p = point.coord
            box[:,0]=numpy.minimum(box[:,0],p)
            box[:,1]=numpy.maximum(box[:,0],p)
            vtk_points.InsertNextPoint(p[0],p[1],p[2])
            #vtk_verts.InsertNextCell(cell)
            vtk_verts.InsertNextCell(1)
            vtk_verts.InsertCellPoint(cell)
            if len(point.color)>0:
                vtk_colors.InsertNextTuple3(point.color[0],point.color[1],point.color[2] )
            else:
                vtk_colors.InsertNextTuple3(255,255,255 )
            cell += 1

        self.sceneWidth=max(box[:,1]-box[:,0])



        poly = vtk.vtkPolyData()
        poly.SetPoints(vtk_points)
        poly.SetVerts(vtk_verts) #causes my machine to crash 3 line below
        poly.GetPointData().SetScalars(vtk_colors)

        #print poly# martin de la gorce : causes my machine to crash if i use verts

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(poly)


        #mapper.SetInputConnection( line2.GetOutputPort() )

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor( 0., 0., 1. )
        actor.GetProperty().SetLineWidth( 0)
        actor.GetProperty().SetRepresentationToPoints
        actor.GetProperty().SetPointSize( 5)
        #actor.GetProperty().SetMarkerStyle(vtk.vtkPlotPoints.CIRCLE);# does not work ,found on http://www.itk.org/Wiki/VTK/Examples/Cxx/Plotting/ScatterPlot
        # how do we rander disk instead of small square  for the points ?!
        return actor

    def plotPoints(self,points):

        actor=self.vtk_point_cloud(points)
        self.ren.AddActor(actor)
        self.renWin.Render()


    def plotSurface():
        pass

    def picking():
        pass





class Example(QtGui.QMainWindow):

    def __init__(self):
        super(Example, self).__init__()


        self.viewWidget = vtkMeshWidget(self)


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
            
        faces=[]        
        for t in r.readElementIndexed():
            faces.append(t.list)
           
            

        points =[Point(coord,color=color) for coord,color in zip(vertices,vertexColors)]
        self.viewWidget.plotPoints(points)
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
