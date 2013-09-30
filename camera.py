import numpy
import sys
sys.path.append("../thirdparties/")
from transformations import transformations




class RigidTransform3D():
    """
    >>> T=RigidTransform3D()
    >>> print T
    [[ 1.  0.  0.  0.]
     [ 0.  1.  0.  0.]
     [ 0.  0.  1.  0.]]
    >>> T=RigidTransform3D(euler=[0,numpy.pi,0],t=[0,0,0])
    >>> print T
    [[ -1.00000000e+00   0.00000000e+00   1.22464680e-16   0.00000000e+00]
     [ -0.00000000e+00   1.00000000e+00   0.00000000e+00   0.00000000e+00]
     [ -1.22464680e-16  -0.00000000e+00  -1.00000000e+00   0.00000000e+00]]
    >>> print T.inverse()
    [[ -1.00000000e+00  -0.00000000e+00  -1.22464680e-16  -0.00000000e+00]
     [  0.00000000e+00   1.00000000e+00  -0.00000000e+00  -0.00000000e+00]
     [  1.22464680e-16   0.00000000e+00  -1.00000000e+00  -0.00000000e+00]]
    """      
        
    def __init__(self,R=None,t=None,euler=None,check_rotation=True,fix_rotation=False):       
        self.Rt=numpy.empty((3,4),dtype=numpy.double)
        if R is not None:
            if euler is not None:
                print 'conflicting rotation parmater, you should use either R or euler but not both'
                raise()
            if fix_rotation:
                    s,v,d=numpy.linalg.svd(R) 
                    R=s.dot(d)
                    # i am no sure this is the best way to project onto SO3
                    
            self.Rt[:,0:3]=R
    
                
            if check_rotation:
                    # this check can slow down hings , if we are sure that the matrix is going to be a rotation matrix we can disable that check 
                    assert (numpy.linalg.norm(self.Rt[:,0:3].T.dot(self.Rt[:,0:3])-numpy.eye(3, dtype=numpy.float64))<1e-8) #should check the matrix is a rotation matrix
                    assert (numpy.linalg.det(self.Rt[:,0:3])>0)                 
        elif euler is not None:
            self.Rt[:,0:3]=transformations.euler_matrix(euler[0],euler[1],euler[2])[:3,:3]
        else:
            self.Rt[:,0:3]=numpy.eye(3, dtype=numpy.float64)
        if t is None:
            self.Rt[:,3]=0
        else:
            self.Rt[:,3]=t  
            
         
        
    def get_rotation(self):
        return self.Rt[:,0:3]
    
    def get_translation(self):
        return self.Rt[:,3]   
    
    def get_matrix34(self):
        return self.Rt   
    
    def apply(self,points):
        return points.dot(self.Rt[:,0:3].T)+self.Rt[:,3]  
        
    
    def inverse(self):          
        return RigidTransform3D(self.get_rotation().T,-self.get_rotation().T.dot(self.get_translation()),check_rotation=False)
    
    def __repr__(self):
        return str(self.Rt)    
  
    

class Camera():
    """This implement a projective camera using classical computer vision conventions
    the camera internal paramter are represented using a 3 by 3 matrix 
    and the camera extern paramter are represented as a rigid 3D transform    
    >>> C=Camera()
    >>> C.setup_internal(focal_in_pixels=640,principal_point=[319.5,219.5])
    >>> C.set_world_to_camera(RigidTransform3D(euler=[0,0,numpy.pi],t=[5,2,3]))
    >>> print C  
    internal parameters:
    [[ 640.     0.   319.5]
     [   0.   640.   219.5]
     [   0.     0.     1. ]]
    world to camera transform:
    [[ -1.00000000e+00  -1.22464680e-16   0.00000000e+00   5.00000000e+00]
     [  1.22464680e-16  -1.00000000e+00   0.00000000e+00   2.00000000e+00]
     [ -0.00000000e+00   0.00000000e+00   1.00000000e+00   3.00000000e+00]]
    >>> p3D=numpy.array([[0,0,0],[3,5,1],[2,1,5],[2,1,6]])
    >>> p,depth=C.project(p3D,getDepth=True)
    >>> print p 
    [[ 1386.16666667   646.16666667]
     [  639.5         -260.5       ]
     [  559.5          299.5       ]
     [  532.83333333   290.61111111]]
    >>> p3D_reconstructed=C.project_inverse(p,depth)
    >>> print p3D_reconstructed
    [[  0.00000000e+00   4.44089210e-16   0.00000000e+00]
     [  3.00000000e+00   5.00000000e+00   1.00000000e+00]
     [  2.00000000e+00   1.00000000e+00   5.00000000e+00]
     [  2.00000000e+00   1.00000000e+00   6.00000000e+00]]
    >>> C.set_world_to_camera(RigidTransform3D(euler=[0,numpy.pi/2,numpy.pi/3],t=[5,2,3]))
    >>> C.set_center_position([2,3,1])
    >>> print C.get_center_position()
    [ 2.  3.  1.]
    """
    def __init__(self):
        
        self.cv_intern=[]# camera inernal paramter matrix. this is a 3 by 3 matrix  
        self.cv_extern=RigidTransform3D()
        self.height=0 # this fields are required only if we use the method set_view_angle
        self.width=0
        
    def __repr__(self):
        return 'internal parameters:\n'+str(self.cv_intern)+'\nworld to camera transform:\n'+str(self.cv_extern)           
        
    def setup_from_total(self,cv_total):
        """decompose 3 by 4 matrix into the product of  extrinsic and intinsic paramters matrices"""
        self.cv_intern=[]
        self.cv_extern=rigidTransfom3D();  
    
    def set_internal_matrix(self,cv_intern):
        assert(numpy.all(cv_intern[2,:]==numpy.array([0,0,1])))
        self.cv_intern=cv_intern
       
        
    def set_world_to_camera(self,cv_extern):
        """this """
        self.cv_extern=cv_extern
        
    def get_center_position(self):
        """return the position of center of the camera in the world coordinate system"""
        return self.cv_extern.inverse().get_translation()
    
    def set_center_position(self,position):           
        self.cv_extern=  RigidTransform3D(R= self.cv_extern.get_rotation(),t=-self.cv_extern.get_rotation().dot(position))   
    
    def get_camera_to_world(self):
        return self.cv_extern.inverse()
    
    def setup_internal(self,focal_in_pixels=None,principal_point=None,pixel_aspect_ratio=1,skew_coefficient=0,width=0,height=0):
        """principal_point: vector of length 2 , principal point location in pixel units"""
        """focal_in_pixel:  scalar focal length expressed in pixel unit ( horizontal pixel unit if the pixel are not square) """
        """pixel aspect ratio"""
        """skew coefficient (!=0 if the pixel axis are not orthogonal)"""
        if principal_point is None:
            # use the center of the image as default principal point, assumin the image sarts at (0,0)
            principal_point=[(height-1)*0.5,(width-1)*0.5]
            
        cv_intern=numpy.array([[focal_in_pixels,skew_coefficient*focal_in_pixels,principal_point[0]],\
                   [0,focal_in_pixels*pixel_aspect_ratio,principal_point[1]],\
                   [0,0,1]])      
        self.set_internal_matrix(cv_intern)
        self.width=width
        self.height=height
    
        
    def set_view_angle(self):
        """Change the focal length in order to get the desired view angle in the left-right direction""" 
        pass        
    def get_view_angle(self):
        pass
    
    
    def project(self,points3D,getDepth=False):
        """project the point from the world coordinates into the pixel coordinates"""
        assert(points3D.shape[1]==3)
        cv_total=self.cv_intern.dot(self.cv_extern.get_matrix34())
        # points_cam=self.cv_extern.apply(points3D)
        # temp=points_cam.dot(self.cv_intern.T)
        #get homogeneous coordinate
        nbpoints=points3D.shape[0]
        temp=points3D.dot(cv_total[:,0:3].T)+cv_total[:,3]       
        points2D=(temp[:,:2].T/temp[:,2]).T # could try to fidd a better way to do that
        if getDepth:
            return points2D,temp[:,2]
        else:
            return points2D
        
    
    def project_inverse(self,points2D,depths):
        """inverse of the projection : get a 3D point from its pixel coordinates and its disance from the optical center after projection on the camera z axis """
        cv_intern_inv=numpy.linalg.inv(self.cv_intern)
        p3d_cam=points2D.dot(cv_intern_inv[:,:2].T)+cv_intern_inv[:,2]
        p3d_cam=(p3d_cam.T*depths).T# could try to fidd a better way to do that
        p3d_world=self.cv_extern.inverse().apply(p3d_cam)
        return p3d_world
    

    
    def convert_to_VTK(self):
        import vtk
        pass
        
    def convert_to_OpenGL(self):
        pass
    
    def convert_from_OpenGL(self):
        pass
    
    
    
class CameraViewer(Camera):
    # class that have extra fields like rotation_center,target etc to help manipulaion in a viewer
    def __init__():
        pass
    def lookat(): 
        """similar to the GLUT lookat ?"""
        pass
    def get_target():
        pass
    def set_target():
        pass
   
    
    def image_corners(self,depth):    # duplicated with vtkBundlerReaxer in my photogrammetry toolbox        
        points2D=numpy.array([[0,0],[self.width,0],[self.width,self.height],[0,self.height]])
        return project_inverse(self,points2D,depths)
    
    def vtkActorPlot():
        #generate a camera plot suitabel for a vtk scene
        pass
   


class CameraOpengGL():
    def __init__():
        self.viewport
        pass
    
    
def _test():
    import doctest
    doctest.testmod()
        
if __name__ == '__main__':
    _test()
   

        
        
    