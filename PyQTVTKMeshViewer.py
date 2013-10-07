# inpired by
# PyQT + OpenGL :
#   http://www.siafoo.net/snippet/316
#   http://pyqglviewer.gforge.inria.fr/wiki/doku.php?id=examples # could not install it....
# QT file loader
# collada example print_collada_info.py
# could have a look at http://rossant.github.com/galry/ that seem to be able to plot multi miliions of points in python

import sys
from PyQt4 import QtGui,QtCore
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

class CutingPlanesWidget(QtGui.QWidget):
    def __init__(self,viewWidget):
	    super(CutingPlanesWidget, self).__init__()
	    vbox = QtGui.QVBoxLayout()
	    self.xSlider = self.createSlider(viewWidget.setXCuttingPlane)
	    self.ySlider = self.createSlider(viewWidget.setYCuttingPlane)
	    self.zSlider = self.createSlider(viewWidget.setZCuttingPlane)
	    vbox.addWidget(self.xSlider)
	    vbox.addWidget(self.ySlider)
	    vbox.addWidget(self.zSlider)
	    self.setLayout(vbox)


    def createSlider(self, setterSlot): # coied from grbber.py example from pyside
	    slider = QtGui.QSlider(QtCore.Qt.Horizontal)
	    maxrange=1000
	    slider.setRange(0, maxrange)
	    slider.setSingleStep(10)
	    slider.setPageStep(10)
	    slider.setTickInterval(100)
	    slider.setTickPosition(QtGui.QSlider.TicksRight)
	    slider.setValue(maxrange)
	    slider.valueChanged.connect(setterSlot)
	    #changedSignal.connect(slider.setValue)

	    return slider


class labellingPanelWidget(QtGui.QWidget):
    def __init__(self,listLabels,function):
		super(labellingPanelWidget, self).__init__()



		vbox = QtGui.QVBoxLayout()
		self.radioGroup = QtGui.QButtonGroup(self)
		self.radioGroup.setExclusive(True)

		bIsFirst=True

		for i,row in enumerate(listLabels):
		    radio = QtGui.QRadioButton(row)

		    #radio .toggled.connect(self.callback)
		    self.radioGroup.addButton(radio, i)
		    if bIsFirst:
			    radio.setChecked(True)
			    bIsFirst = False
		    vbox.addWidget(radio)
		self.function=function
		self.connect(self.radioGroup,QtCore.SIGNAL("buttonClicked(int)"),self.callback)

		#radioGroup.buttonClicked[QtGui.QAbstractButton].connect(self.callback)
		self.setLayout(vbox)
    def callback(self,id):
	self.function(id)





def numpyArrayToVtkUnsignedCharArray(A):
    vtk_array = vtk.vtkUnsignedCharArray()
    vtk_array.SetNumberOfComponents(3)
    cell = 0
    for i in range(A.shape[0]):
	vtk_array.InsertNextTuple3(A[i,0],A[i,1],A[i,2] )
    return vtk_array




class vtkMeshWidget ():
    def __init__(self,MainWindow):

        self.centralWidget = QtGui.QWidget(MainWindow)

        self.gridlayout = QtGui.QGridLayout(self.centralWidget)
        self.gridlayout.setMargin(0)
	single_window=True # true does not work on linux , not sure why
	if single_window:
	    self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)
	    self.gridlayout.addWidget(self.vtkWidget, 0, 0)
	    MainWindow.statusBar() # for some reason this line is necessary to avoid a silent crash on linux when executing self.renWin.Render()
	else:
	    self.vtkWidget = QVTKRenderWindowInteractor()
	    self.vtkWidget.show()

        
        self.cuttingPlanes=[]
        MainWindow.setCentralWidget(self.centralWidget)







        self.renWin= self.vtkWidget.GetRenderWindow()
        self.renWin.PolygonSmoothingOn()
        self.renWin.LineSmoothingOn()
        self.renWin.PointSmoothingOff()
	# self.renWin.PointSmoothingOff()# will draw antialiased circles but assuming that the background is black even if there are draxn point or primitive behind
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


	self.iren.SetRenderWindow(self.renWin)
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.iren.AddObserver("MiddleButtonPressEvent", self.MiddleButtonEvent)
        self.iren.AddObserver("KeyPressEvent", self.Keypressed)
        self.iren.AddObserver("KeyReleaseEvent", self.Keypressed)
	

	self.iren.Initialize()
	self.renWin.Render()
        self.iren.Start()



	self.renWin.Render()
	self.box=numpy.array([[0,1],[0,1],[0,1]])
        self.lastPickedPoint=[]
	self.box=numpy.zeros(shape=(3,2),dtype=float)
	self.box[:,0]=numpy.inf
	self.box[:,1]=-numpy.inf
	self.boxWithOffset=numpy.zeros(shape=(3,2),dtype=float)

    def AddCuttingPlanesWidget(self):
	self.cutingPlanesWidget=CutingPlanesWidget(self)
	self.gridlayout.addWidget(self.cutingPlanesWidget, 1, 0)
        self.cuttingPlanesVtk = vtk.vtkPlaneCollection()
	
	self.cuttingPlaneX=self.addCuttingPlane([0,0,0],[-1,0,0])
	self.cuttingPlaneY=self.addCuttingPlane([0,0,0],[0,-1,0])
	self.cuttingPlaneZ=self.addCuttingPlane([0,0,0],[0,0,-1])		
    def SetInteractorStyle(self,style):
	if style=='Terrain':
	    self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTerrain())
	elif style=='TrackballCamera':
	    self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
	else:
	    self.iren.SetInteractorStyle(style)

    def MiddleButtonEvent(self,obj, event):
        (x,y) = self.iren.GetEventPosition()
        self.renWin.Render()
        idcell,point,idactor=self.pickCell(x,y)
        if idcell!=[]:
            print 'picked cell '+str(idcell) + 'on actor '+ str(idactor)
            self.lastPickedPoint=point

    def Keypressed(self,obj, event):
        print "coucou"
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






    def plotPoints(self,points,colors=[]):

        # look here for vtk examples in python http://www.vtk.org/Wiki/VTK/Examples/Python

        vtk_points = vtk.vtkPoints()
        vtk_verts = vtk.vtkCellArray()
        vtk_colors = vtk.vtkUnsignedCharArray()
        vtk_colors.SetNumberOfComponents(3)
        vtk_colors.SetName( "Colors")
        cell = 0



	if  isinstance(points[0],Point):
	    for point in points:
		p = point.coord
		self.box[:,0]=numpy.minimum(self.box[:,0],p)
		self.box[:,1]=numpy.maximum(self.box[:,1],p)
		vtk_points.InsertNextPoint(p[0],p[1],p[2])
		#vtk_verts.InsertNextCell(cell)
		vtk_verts.InsertNextCell(1)
		vtk_verts.InsertCellPoint(cell)
		if len(point.color)>0:
		    vtk_colors.InsertNextTuple3(point.color[0],point.color[1],point.color[2] )
		else:
		    vtk_colors.InsertNextTuple3(255,255,255 )
		cell += 1
	else: # allow to have points as simple numpy array
	    for p in points:
		self.box[:,0]=numpy.minimum(self.box[:,0],p)
		self.box[:,1]=numpy.maximum(self.box[:,1],p)
		vtk_points.InsertNextPoint(p[0],p[1],p[2])
		#vtk_verts.InsertNextCell(cell)
		vtk_verts.InsertNextCell(1)
		vtk_verts.InsertCellPoint(cell)
		if colors==[]:
		    vtk_colors.InsertNextTuple3(255,255,255 )
		else :
		    vtk_colors.InsertNextTuple3(colors[cell,0],colors[cell,1],colors[cell,2] )
		cell += 1

        self.sceneWidth=max(self.box[:,1]-self.box[:,0])



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
        actor.GetProperty().SetLineWidth(0)
        actor.GetProperty().SetRepresentationToPoints
        actor.GetProperty().SetPointSize( 5)
	actor.SetOrigin(actor.GetCenter())
        #actor.GetProperty().SetMarkerStyle(vtk.vtkPlotPoints.CIRCLE);# does not work ,found on http://www.itk.org/Wiki/VTK/Examples/Cxx/Plotting/ScatterPlot
        # how do we rander disk instead of small square  for the points ?!


        self.ren.AddActor(actor)

	if self.ren.GetActors().GetNumberOfItems()==1:
	    self.recenterCamera()
	self.updateBoxWithOffset()
	self.resetCuttingPlanes()
	self.refreshCuttingPLanes()
        self.renWin.Render()

        return actor




    def updateBoxWithOffset(self):
	self.boxWithOffset[:,0]=self.box[:,0]-1e-5
	self.boxWithOffset[:,1]=self.box[:,1]+1e-5

    def plotSurface(self,points,faces,faceColors=[]):


        vtk_points = vtk.vtkPoints()
        vtk_verts = vtk.vtkCellArray()
        vtk_triangles = vtk.vtkCellArray()
        vtk_colors = vtk.vtkUnsignedCharArray()
        vtk_colors.SetNumberOfComponents(3)
        vtk_colors.SetName( "Colors")
        cell = 0




        for point in points:
            p = point.coord
            self.box[:,0]=numpy.minimum(self.box[:,0],p)
            self.box[:,1]=numpy.maximum(self.box[:,1],p)
            vtk_points.InsertNextPoint(p[0],p[1],p[2])

	self.updateBoxWithOffset()

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
	#actor.GetProperty().SetColor( 0., 0., 1. )

        #actor.GetProperty().SetOpacity(0.7) need to do depth sorting : http://code.google.com/p/pythonxy/source/browse/src/python/vtk/DOC/Examples/VisualizationAlgorithms/DepthSort.py?name=v2.6.6.0&r=001d041959c95a363f4f247643ce759a0a2eb1f6
        actor.GetProperty().SetLineWidth( 1)


	actor.GetProperty().EdgeVisibilityOff();
	actor.GetProperty().SetEdgeColor(0,0,0);
        #actor.GetProperty().SetMarkerStyle(vtk.vtkPlotPoints.CIRCLE);# does not work if we use self.renWin.PointSmoothingOff() ,
	# found on http://www.itk.org/Wiki/VTK/Examples/Cxx/Plotting/ScatterPlot
        # how do we rander disk instead of small square  for the points ?!


        self.ren.AddActor(actor)


	#Alternative method to display the edges
	#inspired from http://stackoverflow.com/questions/7548966/how-to-display-only-triangle-boundaries-on-textured-surface-in-vtk
	#++++++++++++++++++++++++++++++++++++++++++++++++
	#Get the edges from the mesh
	#edges = vtk.vtkExtractEdges()
	#edges.ColoringOff()
	#edges.SetInput(poly)
	#edge_mapper = vtk.vtkPolyDataMapper()
	#edge_mapper.SetInput(edges.GetOutput())

	## Make an actor for those edges
	#edge_actor = vtk.vtkActor()
	#edge_actor.SetMapper(edge_mapper)

	## Make the actor red (there are other ways of doing this also)
	#edge_actor.GetProperty().SetColor(0,0,0)

	#self.ren.AddActor(edge_actor)

	### Avoid z-buffer fighting
	vtk.vtkPolyDataMapper().SetResolveCoincidentTopologyToPolygonOffset()


	if self.ren.GetActors().GetNumberOfItems()==1:
	    self.recenterCamera()

	self.resetCuttingPlanes()
	self.refreshCuttingPLanes()
        self.renWin.Render()
	return actor.GetAddressAsString(None)

    def plotPolyLines(self,listPolyLines,color=[0,0,0]):
		# if the purpose is to display edges of polygons on top of the rendered polygon
	        # this mighr not work very well due to z buffer conflicts
	        # coudl have a looek at http://cgg-journal.com/2008-2/06/index.html

		vtk_points = vtk.vtkPoints()
		vtk_lines = vtk.vtkCellArray()




		idp=0
		for polyLine in listPolyLines:
		    vtkPolyLine=vtk.vtkPolyLine()
		    vtkPolyLine.GetPointIds().SetNumberOfIds(len(polyLine)+1);
		    for i, p in enumerate(polyLine):
			vtk_points.InsertNextPoint(p[0],p[1],p[2])
			vtkPolyLine.GetPointIds().SetId(i,idp)
			idp+=1
			self.box[:,0]=numpy.minimum(self.box[:,0],p)
			self.box[:,1]=numpy.maximum(self.box[:,1],p)
		    p =polyLine[0]
		    vtk_points.InsertNextPoint(p[0],p[1],p[2])

		    i=len(polyLine)
		    vtkPolyLine.GetPointIds().SetId(i,idp)
		    idp+=1

		    vtk_lines.InsertNextCell(vtkPolyLine)


		poly = vtk.vtkPolyData()
		poly.SetPoints(vtk_points)
		poly.SetLines(vtk_lines)



		mapper = vtk.vtkPolyDataMapper()
		mapper.SetInput(poly)


		actor = vtk.vtkActor()
		actor.SetMapper(mapper)

		#actor.GetProperty().SetOpacity(0.7) need to do depth sorting : http://code.google.com/p/pythonxy/source/browse/src/python/vtk/DOC/Examples/VisualizationAlgorithms/DepthSort.py?name=v2.6.6.0&r=001d041959c95a363f4f247643ce759a0a2eb1f6
		#actor.GetProperty().SetLineWidth( 1)

		actor.GetProperty().EdgeVisibilityOff()
		actor.GetProperty().SetEdgeColor(1, 0,0)
		actor.GetProperty().SetColor( color[0], color[1], color[1] )

		self.ren.AddActor(actor)



		### Avoid z-buffer fighting
		vtk.vtkPolyDataMapper().SetResolveCoincidentTopologyToPolygonOffset()# polygon offSet parameters are shared by all the mappers


		if self.ren.GetActors().GetNumberOfItems()==1:
		    self.recenterCamera()


		self.resetCuttingPlanes()
		self.refreshCuttingPLanes()
		self.renWin.Render()
    def recenterCamera(self):
	self.sceneWidth=max(self.box[:,1]-self.box[:,0])
	self.center=0.5*(self.box[:,1]+self.box[:,0])

	self.ren.GetActiveCamera().SetPosition( self.center[0], self.center[1], self.center[2]+self.sceneWidth)
	self.ren.GetActiveCamera().SetFocalPoint( self.center[0], self.center[1], self.center[2])
	

    def plotObjFile(self,fame):

        reader= vtk.vtkOBJReader()
        reader.SetFileName(fame)
        mapper=vtk.vtkPolyDataMapper()
        self.reader=reader
        mapper.SetInputConnection(reader.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.ren.AddActor(actor)
        self.center=[0,0,0]
	self.resetCuttinPlanes()
	self.refreshCutingPLanes()
        self.renWin.Render()

    def resetCuttingPlanes(self):
	if  self.cuttingPlanes!=[]:
	    self.setXCuttingPlane(self.cutingPlanesWidget.xSlider.value())
	    self.setYCuttingPlane(self.cutingPlanesWidget.ySlider.value())
	    self.setZCuttingPlane(self.cutingPlanesWidget.zSlider.value())


    def setXCuttingPlane(self,value):
	pass
	v1=1-float(value)/1000
	v2=float(value)/1000
	self.cuttingPlaneX.SetOrigin(self.boxWithOffset[0,0]*v1+self.boxWithOffset[0,1]*v2, 0, 0)
	self.renWin.Render() #seems to be needed otherwise it doesn't  refresh well the 3D display, but slow down refreshment of the slider itself :(
    def setYCuttingPlane(self,value):
	v1=1-float(value)/1000
	v2=float(value)/1000
	self.cuttingPlaneY.SetOrigin(0, self.boxWithOffset[1,0]*v1+self.boxWithOffset[1,1]*v2, 0)
	self.renWin.Render()#seems to be needed otherwise it doesn't  refresh well the 3D display, but slow down refreshment of the slider itself :(
    def setZCuttingPlane(self,value):
	v1=1-float(value)/1000
	v2=float(value)/1000
	self.cuttingPlaneZ.SetOrigin(0, 0, self.boxWithOffset[2,0]*v1+self.boxWithOffset[2,1]*v2)
	self.renWin.Render()#seems to be needed otherwise it doesn't  refresh well the 3D display, but slow down refreshment of the slider itself :(

    def refreshCuttingPLanes(self):
	if  self.cuttingPlanes!=[]:
	    actors=self.ren.GetActors()
	    actors.InitTraversal()
	    for i in range(actors.GetNumberOfItems()):
		a=actors.GetNextActor()
		#cutter.AddInputConnection(self.reader.GetOutputPort())# is need to ba able to generate a vtkAlgorithmOutput from vtkPolyData , cannot find out how to do that
		#cutter.AddInput(a.GetMapper().GetInput())
		a.GetMapper().SetClippingPlanes(self.cuttingPlanesVtk)

    def addCuttingPlane(self,origin,normal):


        #create cutter
        #cutter=vtk.vtkCutter()
        # clipper = vtk.vtkClipPolyData()
        #cutter.SetCutFunction(plane)

        cuttingplane= vtk.vtkPlane()

        cuttingplane.SetOrigin(origin[0], origin[1], origin[2])
        cuttingplane.SetNormal(normal[0], normal[1], normal[2])  # keep everything in direction of normal


        self.cuttingPlanesVtk.AddItem(cuttingplane)
	self.cuttingPlanes=[]
	self.cuttingPlanesVtk.InitTraversal()
	for i in range(self.cuttingPlanesVtk.GetNumberOfItems()):
		self.cuttingPlanes.append(self.cuttingPlanesVtk.GetNextItem())


        self.refreshCuttingPLanes()



        #cutter.Update()
        #cutterMapper=vtk.vtkPolyDataMapper()
        #cutterMapper.SetInputConnection( cutter.GetOutputPort())
        #create plane actor
        #planeActor=vtk.vtkActor()
        #planeActor.GetProperty().SetColor(1.0,1,0)
        #planeActor.GetProperty().SetLineWidth(2)
        #planeActor.SetMapper(cutterMapper)
        #self.ren.AddActor(planeActor)
       # self.renWin.Render()
	return cuttingplane

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

            pickedActorId=cellPicker.GetActor().GetAddressAsString(None)
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
            pickedActorId=[]

        return pickedCellId,p3D,pickedActorId


    def addLabelingPanel(self,listLabels,function):

	    self. labellingPanel=labellingPanelWidget(listLabels,function)

	    self.gridlayout.addWidget(self. labellingPanel, 0, 1)


	   
	 


class MyInteractorStyle(vtk.vtkInteractorStyle):
    def __init__(self,parent=None):
    
	self.AddObserver("LeftButtonPressEvent", self.ButtonEvent)
	self.AddObserver("LeftButtonReleaseEvent",  self.ButtonEvent)
	self.AddObserver("MiddleButtonPressEvent",  self.ButtonEvent)
	self.AddObserver("MiddleButtonReleaseEvent",  self.ButtonEvent)
	self.AddObserver("RightButtonPressEvent",  self.ButtonEvent)
	self.AddObserver("RightButtonReleaseEvent",  self.ButtonEvent)
	self.AddObserver("KeyPressEvent", self.KeyEvent)
	self.AddObserver("KeyReleaseEvent", self.KeyEvent)
	
	self.Rotating = 0
	self.Panning  = 0
	self.Zooming  = 0
	self.rotate_object = False
	self.AddObserver("MouseMoveEvent", self.MouseMoveEvent)
	   
	
    def ButtonEvent(self,obj, event):
	
	if event == "LeftButtonPressEvent":
	    self.Rotating = 1
	elif event == "LeftButtonReleaseEvent":
	    self.Rotating = 0
	elif event == "MiddleButtonPressEvent":
	    self.Panning = 1
	elif event == "MiddleButtonReleaseEvent":
	    self.Panning = 0
	elif event == "RightButtonPressEvent":
	    self.Zooming = 1
	elif event == "RightButtonReleaseEvent":
	    self.Zooming = 0
    
     
    def MouseMoveEvent(self,obj,eventName):
	
	if self.Rotating or  self.Panning or self.Zooming:
	    iren = obj.GetInteractor()
	    renWin=iren.GetRenderWindow()
	    ren=renWin.GetRenderers().GetFirstRenderer()	
	    camera=ren.GetActiveCamera()	    
	    lastXYpos = iren.GetLastEventPosition()
	    lastX = lastXYpos[0]
	    lastY = lastXYpos[1]
	  
	    xypos = iren.GetEventPosition()
	    x = xypos[0]
	    y = xypos[1]
	  
	    center = renWin.GetSize()
	    centerX = center[0]/2.0
	    centerY = center[1]/2.0	    
		  
	    if self.Rotating: 
		if  self.rotate_object:
		   
		    actors=ren.GetActors()
		    actor=actors.GetLastActor()
		    
		    actor.GetPosition()		
		    actor.GetOrientation()
		    actor.RotateZ(lastX-x)
		    #actor.RotateY(lastY-y)
		    renWin.Render()	
		else:
		   	
		    camera.Azimuth(lastX-x)
		    camera.Elevation(lastY-y)
		    #camera.OrthogonalizeViewUp()	 
		    camera.SetViewUp((0.0,0.0,1.0))
		    renWin.Render()		    
	    
	    if  self.Panning:
		if  self.rotate_object:
		    actors=ren.GetActors()
		    actor=actors.GetLastActor()
		    pos=actor.GetPosition()
		    viewDir=camera.GetViewPlaneNormal()
		    n=numpy.sqrt(viewDir[0]**2+viewDir[1]**2)
		    viewDir2D= numpy.array([viewDir[0]/n,viewDir[1]/n,0])
		    dir2=numpy.cross(viewDir2D,numpy.array([0,0,1]))
		    rotation=numpy.column_stack((dir2,viewDir2D))
		    displacement=rotation.dot(numpy.array([(lastX-x)/100.,(lastY-y)/100.]))
		    newpos=(pos[0]+displacement[0],pos[1]+displacement[1],pos[2]+displacement[2])		    
		    actor.SetPosition(newpos)	
		    renWin.Render()
		else:
		    FPoint = camera.GetFocalPoint()
		    FPoint0 = FPoint[0]
		    FPoint1 = FPoint[1]
		    FPoint2 = FPoint[2]
	
		    PPoint = camera.GetPosition()
		    PPoint0 = PPoint[0]
		    PPoint1 = PPoint[1]
		    PPoint2 = PPoint[2]
	
		    ren.SetWorldPoint(FPoint0, FPoint1, FPoint2, 1.0)
		    ren.WorldToDisplay()
		    DPoint = ren.GetDisplayPoint()
		    focalDepth = DPoint[2]
	
		    APoint0 = centerX+(x-lastX)
		    APoint1 = centerY+(y-lastY)
		    
		    ren.SetDisplayPoint(APoint0, APoint1, focalDepth)
		    ren.DisplayToWorld()
		    RPoint = ren.GetWorldPoint()
		    RPoint0 = RPoint[0]
		    RPoint1 = RPoint[1]
		    RPoint2 = RPoint[2]
		    RPoint3 = RPoint[3]
	    
		    if RPoint3 != 0.0:
			RPoint0 = RPoint0/RPoint3
			RPoint1 = RPoint1/RPoint3
			RPoint2 = RPoint2/RPoint3
		
		    camera.SetFocalPoint( (FPoint0-RPoint0)/2.0 + FPoint0,
			                  (FPoint1-RPoint1)/2.0 + FPoint1,
			                  (FPoint2-RPoint2)/2.0 + FPoint2)
		    camera.SetPosition( (FPoint0-RPoint0)/2.0 + PPoint0,
			                (FPoint1-RPoint1)/2.0 + PPoint1,
			                (FPoint2-RPoint2)/2.0 + PPoint2)
		    renWin.Render()
	    if  self.Zooming:
		dollyFactor = pow(1.02,(0.5*(y-lastY)))
		if camera.GetParallelProjection():
		    parallelScale = camera.GetParallelScale()*dollyFactor
		    camera.SetParallelScale(parallelScale)
		else:
		    camera.Dolly(dollyFactor)
		    ren.ResetCameraClippingRange()
	    
		renWin.Render()     
	
    def KeyEvent(self,obj,eventName):
        iren = obj.GetInteractor()		    

        key = iren.GetKeyCode()
	KeyPressed=eventName=='KeyPressEvent'
	if eventName=='KeyPressEvent':
	    print "pressed key "+  key
	else:
	    print "released key "+  key   
	if KeyPressed and (key=='q' or key=='Q'):
	    self.rotate_object=~self.rotate_object
	    
	if key=='z':	      
	    renWin=iren.GetRenderWindow()
	    ren=renWin.GetRenderers().GetFirstRenderer()	
	    camera=ren.GetActiveCamera()
	    camera.SetViewUp((0.0,0.0,1.0))
	    camera.OrthogonalizeViewUp()	  
	    v=camera.GetViewUp()
	    renWin.Render()
	pass	
    




class Example(QtGui.QMainWindow):

    def __init__(self):
        super(Example, self).__init__()


        self.viewWidget = vtkMeshWidget(self)

	

        self.viewWidget.SetInteractorStyle(MyInteractorStyle())
	#self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTerrain())
	self.viewWidget.iren.AddObserver("MouseWheelForwardEvent", self.myWheelCallback)
	self.viewWidget.iren.AddObserver("MouseWheelBackwardEvent", self.myWheelCallback)
	self.viewWidget.iren.AddObserver("keyPressedEvent", self.myKeyPressedCallback)
	
        #self.statusBar()


        openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
	openFile.setShortcut('Ctrl+O')
	openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.openFileGui)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('File dialog')
        self.show()
	
	self.pointClouds=[]
	

	
    def myWheelCallback(self,a,eventName):
	if self.pointClouds!=[]:
	    for pointCloud in self.pointClouds:
		pointsActor=pointCloud['pointsActor']
		pointSize=pointsActor.GetProperty().GetPointSize()
	    if eventName=='MouseWheelForwardEvent':
		pointSize=pointSize+1
	    else:
		pointSize=pointSize-1
		if pointSize<1:
		    pointSize=1

	    mapper=pointsActor.GetProperty().SetPointSize( pointSize)
	    self.viewWidget.renWin.Render()
    def myKeyPressedCallback(self,obj,eventName): 

	print "pressed key "+obj.GetKeyCode()
	PyQTVTKMeshViewer.vtkMeshWidget.Keypressed(self,obj, event)
	if obj.GetKeyCode()=='r':# perform a virtual scan
		 self.viewWidget.recenterCamera()	   
 
	    
    def openFileGui(self):

        fname = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file',       os.getcwd()))
	self.openFile(fname)
	
    def openFile(self,fname):

        suffix = fname[fname.rindex("."):].lower()
	if suffix=='.pcd' or suffix=='.ply':
	    # this is a point cloud
	    import pointCloudIO
	    if suffix=='.pcd':
		points,colors, data,maps=pointCloudIO.loadPCD(fname,default_color=(numpy.random.rand(3)*200+50).astype(int))
	    elif suffix=='.ply':
		points,colors, data=pointCloudIO.loadPLY(fname)
		maps=dict()

	    #self.viewWidget.plotPoints(points.reshape((-1,3)))
	    
	    
	   
	    pointsActor=self.viewWidget.plotPoints(points.reshape((-1,3)),colors=colors.reshape((-1,3)))

	    vtkcolors_fields=dict()

	    vtkcolors_fields['rgb']=numpyArrayToVtkUnsignedCharArray(colors)

	    for key in data.keys():
		    if issubclass(data[key].dtype.type, numpy.integer):
			colormap=(numpy.random.rand(numpy.max(data[key])+1,3)*255).astype(int)
			newcolors=colormap[data[key]]
			vtk_colors =numpyArrayToVtkUnsignedCharArray(newcolors)
		    else:
			vtk_colors=[]
			print 'no yet coded'
			continue
		    vtkcolors_fields[key]=vtk_colors
	    pointCloud={'pointsActor': pointsActor,'vtkcolors_fields':vtkcolors_fields}
	    self.pointClouds.append(pointCloud)
	    self.viewWidget.recenterCamera()
	   


	    def update_colors(id):

		mapper=self.pointsActor.GetMapper()
		poly=mapper.GetInput()
		key=vtkcolors_fields.keys()[id]
		if vtkcolors_fields[key]!=[]:
		    poly.GetPointData().SetScalars(vtkcolors_fields[key])
		    self.viewWidget.renWin.Render()
		    if maps.has_key(key):
			pass # should display the legend

	    self.viewWidget.addLabelingPanel(vtkcolors_fields.keys(),update_colors)


	else:

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
		faces.append([int(iv) for iv in t.list])



	    points =[Point(coord,color=color) for coord,color in zip(vertices,vertexColors)]
	    self.viewWidget.plotPoints(points)
	    self.viewWidget.plotSurface(points,faces)
	    #self.viewWidget.plotObjFile (fname)
	    #self.viewWidget.addCuttingPlane([0,0,0],[-1,0,0])
	    #self.viewWidget.getCuttingPlanes()
	    # creat numpy arrays
	    # vertices
	    # normals
	    # faces

	    #self.glWidget.loadCollada(fname)




def main():

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    ex.openFile('/media/truecrypt1/scene_labelling_rgbd/data/home/models/scene22_m1.pcd')
    ex.openFile('/media/truecrypt1/scene_labelling_rgbd/data/home/models/scene31_m2.pcd')
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
