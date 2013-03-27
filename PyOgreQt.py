# from http://wiki.python-ogre.org/index.php/CodeSnippets_PyQtv4_Ogre_Widget
from PyQt4 import QtOpenGL,QtCore
import ogre.renderer.OGRE as Ogre
from PyQt4 import QtGui
import sys

class OgreWidget(QtOpenGL.QGLWidget):
    #widget specific metods---------------------------------------------------------------------
    def __init__(self,parent = None):
        QtOpenGL.QGLWidget.__init__(self,parent)
        self.root = None
        self.camera = None
        self.renderWindow = None
        self.sceneManager = None
        self.viewport = None



    def initializeGL(self):
        self.createRoot()
        self.loadPlugins()
        self.defineResources()
        self.setupRenderSystem()
        self.createRenderWindow("test")
        wnid = self.renderWindow.getCustomAttributeFloat("WINDOW")
        self.create(wnid)
        self.setAttribute(QtCore.Qt.WA_PaintOnScreen,True)
        self.createCamera()
        self.createViewport()
        self.loadScene()

        #needed to update the widget every 50 mS. (i.e. 20 fps)
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer,QtCore.SIGNAL("timeout()"),self,QtCore.SLOT("update()"))
        self.timer.start(100)

    def paintGL(self):
        self.root.renderOneFrame()
        self.animationStates.addTime(1)

    def resizeGL(self,widht,height):
        self.renderWindow.windowMovedOrResized()

    #ogre specific metods------------------------------------------------------------------------
    def createRoot(self):
        #create root object without any configuration file
        self.root = Ogre.Root("","","")

    def loadPlugins(self):
        #add any other needed plugin here
        self.root.loadPlugin("plugins/RenderSystem_GL")

    def defineResources(self):
        #add any other needed resource here
        self.root.addResourceLocation("media/models","FileSystem","General")
        Ogre.ResourceGroupManager.getSingleton().initialiseAllResourceGroups()

    def setupRenderSystem(self):
        renderSystemList = self.root.getAvailableRenderers() #list of aviable render systems
        for rs in renderSystemList:
            rsName = rs.getName()
            if rsName == "OpenGL Rendering Subsystem":       #select OpenGL Render System
                self.root.setRenderSystem(rs)
                self.root.initialise(False)                  #initalise Ogre without creating render window

        self.sceneManager = self.root.createSceneManager(Ogre.ST_GENERIC)

    def createRenderWindow(self,name):
        opts = Ogre.NameValuePairList()
        opts['externalWindowHandle'] = str(int(self.winId())) #handle of the widget
        opts['externalGLControl'] = "true"                    #the OpenGL context is get from Qt
        self.renderWindow = self.root.createRenderWindow(name,self.width(),self.height(),False,opts)
        self.renderWindow.setActive(True)



    def createCamera(self):
        self.camera = self.sceneManager.createCamera('Camera')
        self.camera.lookAt(Ogre.Vector3(0, 0, 0))
        self.camera.NearClipDistance = 5


    def createViewport(self):
        renderWindow = self.renderWindow
        self.viewport = renderWindow.addViewport(self.camera)
        self.viewport.BackgroundColour = Ogre.ColourValue(255.0, 255.0, 255.0)

    def loadScene(self):
        sceneManager = self.sceneManager
        camera = self.camera
        entity = sceneManager.createEntity('robot', 'robot.mesh')
        sceneManager.getRootSceneNode().createChildSceneNode(Ogre.Vector3(0, 0, 0)).attachObject(entity)
        self.animationStates = entity.getAnimationState('Walk')
        light = sceneManager.createLight('BlueLight')
        light.setPosition (-200, -80, -100)
        light.setDiffuseColour (Ogre.ColourValue(0.5, 0.5, 1.0) )
        self.animationStates.Enabled = True


        light = sceneManager.createLight('GreenLight')
        light.setPosition (0, 0, -100)
        light.setDiffuseColour (0.5, 1.0, 0.5)

        camera.setPosition (100, 50, 100)
        camera.lookAt(-50, 50, 0)

    def cleanUp(self):
        pass
    
    
    
class Example(QtGui.QMainWindow):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()

    def initUI(self):

        self.glWidget =  OgreWidget(self)
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

        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                '/home')
        self.glWidget.loadCollada(fname)




def main():

    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
