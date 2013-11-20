import numpy
import cv2		 
import scipy
from transformations import transformations

def exactNN(a,b):
    idx=numpy.empty(len(a),dtype=numpy.int32)
    distSquared=numpy.empty(len(a),dtype=numpy.float)
    for i,p in enumerate(a): 
        d=numpy.sum((b-p)**2,axis=1)
        idx[i]=numpy.argmin(d)
        distSquared[i]=d[idx[i]]
    return idx,distSquared	


def IterativeClosestPoint(pointsSource,pointsTarget,initalTransform,nbitermax=100,visualizeFunc=None,verbose=False,tol=1e-5,use_scaling=False):
    """implementation of iterative closests point that optimizes only with rotation around the z axis and the slatation in x and y """
    assert(pointsSource.shape[1]==3)
    assert(pointsTarget.shape[1]==3)

    # could subsample scene first 
    # could compute poit-to-convex patches distance
   
    
    sourceRotationCenter=pointsSource.mean(axis=0)
    sourceRotationCenter[2]=0 # we want the rescaled oject to tuch the floor
    #from scipy import spatial
    #kdtree=scipy.spatial.KDTree(pointsTarget)

    flann_params = dict(algorithm=1, trees=4)
    
   
    flann = cv2.flann_Index(pointsTarget, flann_params)
    

    def getParametersFromMatrix(RT,rotation_center):
        angles=transformations.euler_from_matrix(RT)
        assert(angles[0]==0)
        assert(angles[1]==0)			
        translate=RT[:3,3]-(RT[:3,:3].dot(-rotation_center)+rotation_center)
        assert(translate[2]==0)
        parameters=numpy.array((angles[2],translate[0],translate[1]))
        return parameters

    def getMatrixFromParameters(parameters,rotation_center):
        orientation_angles=[0,0,parameters[0]]
        position=numpy.array((parameters[1],parameters[2],0))
        T1=transformations.compose_matrix(translate=-rotation_center)
        R=transformations.compose_matrix(angles=orientation_angles)
        if use_scaling:
            R[:3,:3]=R[:3,:3]*parameters[3:]
            
        T2=transformations.compose_matrix(translate=rotation_center+position)
        RT=transformations.concatenate_matrices(T2,R,T1)			
        return RT	
    
   

    #checking the two functions are consistent
  


    
     
    def transformPointsWithScales(angle_translation_scales):
        scales=angle_translation_scales[3:]
        angle_translation=angle_translation_scales[:3]
        pointsSourceCentered=(pointsSource-sourceRotationCenter)*scales
        RT=transformations.compose_matrix(angles=[0,0,angle_translation[0]])
        translation=numpy.array((angle_translation[1],angle_translation[2],0))
        transformedPoints= (pointsSourceCentered.dot(RT[:3,:3].T)+sourceRotationCenter+translation).astype(numpy.float32)
        return transformedPoints    


    def transformPointsRigid(angle_translation):
        pointsSourceCentered=pointsSource-sourceRotationCenter
        RT=transformations.compose_matrix(angles=[0,0,angle_translation[0]])
        translation=numpy.array((angle_translation[1],angle_translation[2],0))
        transformedPoints= (pointsSourceCentered.dot(RT[:3,:3].T)+sourceRotationCenter+translation).astype(numpy.float32)
        return transformedPoints
    
      
    angle_translation=getParametersFromMatrix(initalTransform,sourceRotationCenter)    
    angle_translation_scales=numpy.hstack((angle_translation,numpy.array([1,1,1])))
    
        
    if use_scaling:
        transformPoints=transformPointsWithScales 
        parameters=  angle_translation_scales
    else:
        transformPoints=transformPointsRigid 
        parameters=  angle_translation  
        
    initalTransform2= getMatrixFromParameters( parameters,sourceRotationCenter)   
    assert(numpy.linalg.norm(initalTransform2- initalTransform)<1e-6)
    
    def residuals(parameters,idx):
        tp=transformPoints(parameters)
        return (tp-pointsTarget[idx.flatten()])
    def residualsFlat(parameters,idx):
        return residuals(parameters,idx).flatten()

    def cost(parameters,idx):
        transformedPoints=transformPoints(parameters)
        r=residualsFlat(parameters,idx)
        return numpy.sum(r**2)		



    import scipy.optimize as optimize
    transformedPoints=transformPoints(parameters)
    idx=exactNN(transformedPoints,pointsTarget)[0] # start with exact matching insead of flann base macgin in order to avoid increase of energy when starting from previous solution
    if verbose:
        print 'initial parameters = '+str(parameters)
    bestcost=numpy.inf
    
    
    for i in range(nbitermax): 
        
        # update matchings
        transformedPoints=transformPoints(parameters)
        prevDistSquared=(residuals(parameters,idx)**2).sum(axis=1)
        idx, distSquared = flann.knnSearch(transformedPoints, 1, params={})
        idx=idx.flatten()
        # detect points where flann failed at providing a better match and perform brute force search for these points
        wrongIds=numpy.nonzero(prevDistSquared<distSquared.flatten())[0]
        if len(wrongIds)>0:
                    idx[wrongIds]=exactNN(transformedPoints[wrongIds],pointsTarget)[0]
       
            
        
        #idx=numpy.array(kdtree.query(transformedPoints)[1])# seels much slower !
        newcost=cost(parameters,idx)
        #assert(bestcost>=newcost-1e-4)	
        if bestcost<newcost+tol:
            break        
        
        
        bestcost=newcost
        if verbose:
            print 'sum of squared error = '+str(bestcost)
        # update rotation and translation
        result = optimize.leastsq(residualsFlat,parameters ,args=(idx),full_output=True,epsfcn=1e-4)
        parameters=result[0]
        newcost=cost(parameters,idx)
        #assert(bestcost>=newcost-1e-4)
        bestcost=newcost	
       
        if verbose:
            print 'sum of squared error = '+str(bestcost)

        M=getMatrixFromParameters(parameters,sourceRotationCenter)
        if visualizeFunc!=None:
            visualizeFunc(M)
            
    M=getMatrixFromParameters(parameters,sourceRotationCenter)
    if visualizeFunc!=None:
        visualizeFunc(M)   
        
    transformedPoints=transformPoints(parameters)          	
    return M,transformedPoints

def IterativeClosestPointPCL(pointsSource,pointsTarget):
    import pcl
    pc_1 = pcl.PointCloud()
    pc_1.from_array(pointsSource)
    pc_2 = pcl.PointCloud()
    pc_2.from_array(pointsTarget)
   
        
    ICP=pcl.IterativeClosestPoint()
    #ICP.setInputSource(pc_1 )
    ICP.setInputCloud(pc_1 )
    ICP.setInputTarget(pc_2 )
    pc_1aligned = pcl.PointCloud()
    ICP.align(pc_1aligned )   
    ICP.hasConverged()
    ICP.getFitnessScore()    
    return ICP.getFinalTransformation(),pc_1aligned