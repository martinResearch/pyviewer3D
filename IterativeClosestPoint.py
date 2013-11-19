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


def IterativeClosestPoint(pointsSource,pointsTarget,initalTransform,nbitermax=10,visualizeFunc=None,):
    """implementation of iterative closests point that optimizes only with rotation around the z axis and the slatation in x and y """
    assert(pointsSource.shape[1]==3)
    assert(pointsTarget.shape[1]==3)

   
    
    sourceRotationCenter=pointsSource.mean(axis=0)

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
        T2=transformations.compose_matrix(translate=rotation_center+position)
        RT=transformations.concatenate_matrices(T2,R,T1)			
        return RT	
    
   
    angle_translation=getParametersFromMatrix(initalTransform,sourceRotationCenter)

    #checking the two functions are consistent
    initalTransform2= getMatrixFromParameters(angle_translation,sourceRotationCenter)
    assert(numpy.linalg.norm(initalTransform2- initalTransform)<1e-6)


    

    


    def transfomPoints(angle_translation):
        pointsSourceCentered=pointsSource-sourceRotationCenter
        RT=transformations.compose_matrix(angles=[0,0,angle_translation[0]])
        translation=numpy.array((angle_translation[1],angle_translation[2],0))
        transformedPoints= (pointsSourceCentered.dot(RT[:3,:3].T)+sourceRotationCenter+translation).astype(numpy.float32)
        return transformedPoints
    def residuals(angle_translation,idx):
        tp=transfomPoints(angle_translation)
        return (tp-pointsTarget[idx.flatten()])
    def residualsFlat(angle_translation,idx):
        return residuals(angle_translation,idx).flatten()

    def cost(angle_translation,idx):
        transformedPoints=transfomPoints(angle_translation)
        r=residualsFlat(angle_translation,idx)
        return numpy.sum(r**2)		



    import scipy.optimize as optimize
    transformedPoints=transfomPoints(angle_translation)
    idx=exactNN(transformedPoints,pointsTarget)[0] # start with exact matching insead of flann base macgin in order to avoid increase of energy when starting from previous solution
    print angle_translation
    bestcost=numpy.inf
    for i in range(nbitermax): 
                # update matchings
                transformedPoints=transfomPoints(angle_translation)
                prevDistSquared=(residuals(angle_translation,idx)**2).sum(axis=1)
                idx, distSquared = flann.knnSearch(transformedPoints, 1, params={})
                idx=idx.flatten()
                # detect points where flann failed at providing a better match and perform brute force search for these points
                wrongIds=numpy.nonzero(prevDistSquared<distSquared.flatten())[0]
                if len(wrongIds)>0:
                            idx[wrongIds]=exactNN(transformedPoints[wrongIds],pointsTarget)[0]
                #idx=numpy.array(kdtree.query(transformedPoints)[1])# seels much slower !
                newcost=cost(angle_translation,idx)
                assert(bestcost>=newcost-1e-4)		
                bestcost=newcost
                print bestcost
                # update rotation and translation
                result = optimize.leastsq(residualsFlat,angle_translation ,args=(idx),full_output=True,epsfcn=1e-4)
                angle_translation=result[0]
                newcost=cost(angle_translation,idx)
                assert(bestcost>=newcost-1e-4)
                bestcost=newcost	
                print bestcost

                M=getMatrixFromParameters(angle_translation,sourceRotationCenter)
                if visualizeFunc!=None:
                    visualizeFunc(M)
              	
    return M
