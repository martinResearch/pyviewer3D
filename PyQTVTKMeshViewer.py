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
        self.renWin= self.vtkWidget.GetRenderWindow()       
        self.renWin.PolygonSmoothingOn() 
        self.renWin.LineSmoothingOn()        
        self.renWin.PointSmoothingOn()
        # it seems that qt disable antialiasing 
        # http://www.vtk.org/pipermail/vtkusers/2008-November/098417.html   
        # http://www.vtk.org/pipermail/vtkusers/2008-November/098415.html
        # self.renWin.SetMultiSamples(0)      
        # self.renWin.SetAAFrames(6)# works on my maching but very slow
        # QtGui.QPainter.Antialiasing
        #glEnable(GL_MULTISAMPLE)
        self.ren = vtk.vtkRenderer()
        self.renWin.AddRenderer(self.ren)
        self.iren = self.renWin.GetInteractor()
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.iren.AddObserver("MiddleButtonPressEvent", self.MiddleButtonEvent)
        self.iren.AddObserver("KeyPressEvent", self.Keypress)
        self.iren.AddObserver("KeyReleaseEvent", self.Keypress)
        self.iren .Initialize()
        self.renWin.Render()
        self.iren.Start()    
        
        self.lastPickedPoint=[]

    def MiddleButtonEvent(self,obj, event):         
        (x,y) = self.iren.GetEventPosition()
        self.renWin.Render()
        idcell,point=self.pickCell(x,y)
        if idcell!=[]:
            print 'picked cell '+str(idcell)         
            self.lastPickedPoint=point

    def Keypress(self,obj, event):
        
        if obj.GetKeyCode()=='c':
            if len(self.lastPickedPoint)>0:
                self.ren.GetActiveCamera().SetFocalPoint(self.lastPickedPoint[0],self.lastPickedPoint[1],self.lastPickedPoint[2])    
                self.renWin.Render()



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






    def plotPoints(self,points):
        
        # look here for vtk examples in python http://www.vtk.org/Wiki/VTK/Examples/Python

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
       

        self.ren.AddActor(actor)
        self.renWin.Render()
        
        
    def plotSurface(self,points,faces,faceColors=[]):
        
        self.faces=faces   
        vtk_points = vtk.vtkPoints()
        vtk_verts = vtk.vtkCellArray()
        vtk_triangles = vtk.vtkCellArray()
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
            
        for idf,f in enumerate(faces):
            # inspired from http://stackoverflow.com/questions/7548966/how-to-display-only-triangle-boundaries-on-textured-surface-in-vtk
            triangle = vtk.vtkTriangle()  
            triangle.GetPointIds().SetId(0,f[0])
            triangle.GetPointIds().SetId(1,f[1])
            triangle.GetPointIds().SetId(2,f[2])   
            if len(faceColors)>0:   
                facecolor=faceColors[idf]
                vtk_colors.InsertNextTuple3(facecolor[0],facecolor[1],facecolor[2] )
            else:
                vtk_colors.InsertNextTuple3(255,255,255 )
            vtk_triangles.InsertNextCell(triangle)
            
         
        
        self.sceneWidth=max(box[:,1]-box[:,0])
        
        

        poly = vtk.vtkPolyData()
        poly.SetPoints(vtk_points)
        #poly.SetVerts(vtk_verts) #causes my machine to crash 3 line below
        poly.SetPolys(vtk_triangles)
       
        poly.GetCellData().SetScalars(vtk_colors)
        poly.Modified()
        if vtk.VTK_MAJOR_VERSION <= 5:
            poly.Update()        
        
        #poly.GetPointData().SetScalars(vtk_colors)

        #print poly# martin de la gorce : causes my machine to crash if i use verts
        #mapper=vtk.vtkCompositeDataGeometryFilter()
 
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(poly)
        #alg=vtk.vtkPolyDataAlgorithm()
        #alg.SetInput(poly)
        #mapper.SetInputConnection(alg.GetOutputPort())        
        

        #mapper.SetInputConnection( line2.GetOutputPort() )

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        #if len(faceColors)==0:
        #    actor.GetProperty().SetColor( 0., 0., 1. )
        
        #actor.GetProperty().SetOpacity(0.7) need to do depth sorting : http://code.google.com/p/pythonxy/source/browse/src/python/vtk/DOC/Examples/VisualizationAlgorithms/DepthSort.py?name=v2.6.6.0&r=001d041959c95a363f4f247643ce759a0a2eb1f6
        actor.GetProperty().SetLineWidth( 0)
        actor.GetProperty().SetRepresentationToPoints
        actor.GetProperty().SetPointSize( 5)
        #actor.GetProperty().SetMarkerStyle(vtk.vtkPlotPoints.CIRCLE);# does not work ,found on http://www.itk.org/Wiki/VTK/Examples/Cxx/Plotting/ScatterPlot
        # how do we rander disk instead of small square  for the points ?!
       

        self.ren.AddActor(actor)
        self.center=0.5*(box[:,1]+box[:,0])
        
        self.ren.GetActiveCamera().SetPosition( self.center[0], self.center[1], self.center[2]+self.sceneWidth)
        self.ren.GetActiveCamera().SetFocalPoint( self.center[0], self.center[1], self.center[2])
        self.renWin.Render()
    
    def addCuttingPlane(self):
        #create a plane to cut,here it cuts in the XZ direction (xz normal=(1,0,0);XY =(0,0,1),YZ =(0,1,0)
        plane=vtk.vtkPlane()
        plane.SetOrigin(0,0,0)
        plane.SetNormal(1,0,0)
         
        #create cutter
        cutter=vtk.vtkCutter()
        # clipper = vtk.vtkClipPolyData()
        cutter.SetCutFunction(plane)
        actors=self.ren.GetActors()
        actors.InitTraversal()
        for i in range(actors.GetNumberOfItems()):
            a=actors.GetNextActor()
            cutter.AddInputConnection(a.GetMapper().GetOutputPort())# is need to ba able to generate a vtkAlgorithmOutput from vtkPolyData , cannot find out how to do that
        cutter.Update()
        cutterMapper=vtk.vtkPolyDataMapper()
        cutterMapper.SetInputConnection( cutter.GetOutputPort())
         
        #create plane actor
        planeActor=vtk.vtkActor()
        planeActor.GetProperty().SetColor(1.0,1,0)
        planeActor.GetProperty().SetLineWidth(2)
        planeActor.SetMapper(cutterMapper)
        self.ren.AddActor(planeActor)
      
    def pickCell(self,x,y): 
        #picker = vtk.vtkPropPicker()
        #picker.PickProp(x, y, self.renderer, EventHandler().get_markers())
        #actor = picker.GetActor()
        #from http://nullege.com/codes/show/src@m@u@MultiScaleSVD-HEAD@icicle_noview_textured.py/599/vtk.vtkCellPicker
        cellPicker = vtk. vtkCellPicker()
        someCellPicked = cellPicker.Pick(x,y,0,self.ren)
        if  someCellPicked:
            pickedCellId = cellPicker.GetCellId()
            p=cellPicker.GetPickedPositions()
            p3D=p.GetPoint(0)
            #actor=cellPicker.GetActor()
            #cells=actor.GetMapper().GetInput().GetPolys()
            #cellsData=cells=actor.GetMapper().GetInput().GetCellData()
            #idList = vtk.vtkIdList()
            #cells.GetNumberOfCells()
            #data=cells.GetData()
            #face=[]
            #for i in range(3):
                #face.append(data.GetValue(4*pickedCellId+i+1))
           
            #plotSurface(self,points,faces,faceColors=[[0,0,1]])   
            
            ##cells.GetCell(pickedCellId,idList)
            ##for i in range(idList.GetNumberOfIds()):
            ##    print idList.GetId(i)# does no work...
        else:
            pickedCellId=[]
            p3D=[]
            
       
        return pickedCellId,p3D

  





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
            faces.append([int(iv)-1 for iv in t.list])
           
        

        points =[Point(coord,color=color) for coord,color in zip(vertices,vertexColors)]
        self.viewWidget.plotPoints(points)
        self.viewWidget.plotSurface(points,faces)
        #self.viewWidget.addCuttingPlane()
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
