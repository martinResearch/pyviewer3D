import numpy as np
from  camera import RigidTransform3D

def savePTX(transform,points,filename):
	"""export data to the leica ptx format"""
	with open(filename, 'w') as f:
		f.write(str(points.shape[0])+'\n')
		f.write(str(points.shape[1])+'\n')
		np.savetxt(f,transform.get_translation().reshape([1,3]),'%.5f')
		np.savetxt(f,transform.get_rotation(),'%.5f')
		np.savetxt(f,transform.Rt,'%.5f')
		np.savetxt(f,transform.get_translation().reshape([1,3]),'%.5f')
		for p in points.reshape([-1,3]):
			np.savetxt(f,np.hstack((p,np.array([1,127,127,127]))).reshape([1,7]),'%.5f %.5f %.5f %d %d %d %d')
			
def loadPTX(filename):
	with open(filename, 'r') as f:
		
		nblines=int(f.readline())

		nbcols=int(f.readline())
		print nblines
		print nbcols		
		points=np.empty((nblines,nbcols))
		#np.loadtxt does not allow yet to specify a number of rows, np ticket 1731. 
		#http://np-discussion.10968.n7.nabble.com/using-loadtxt-for-given-number-of-rows-td3635.html
		translation=np.fromfile(f, sep=' ', count=3) 
		rotation=np.fromfile(f, sep=' ', count=9).reshape(3,3)
		print rotation
		Rt=np.fromfile(f, sep=' ', count=12).reshape(3,4)
		translation=np.fromfile(f, sep=' ', count=3) 
		transform=RigidTransform3D(rotation,translation,fix_rotation=True)
		points_with_color=np.fromfile(f,  sep=' ',count=-1).reshape(-1,7)		
		points=points_with_color[:,:3].reshape((nblines,nbcols,3))		
		colors=points_with_color[:,4:7].reshape((nblines,nbcols,3)).astype(int)
		return points, colors , transform

def savePCD(transform,points,filename,idpolys,polygons,idlabelToMaterial,labelColors):
	"""export data to the Point Cloud Library PCD format
	the file can then be visualized using the pcl executable pcd_viewer that can be called from the terminal
	there seem to be a problem with the exportation of the point colors..."""
	with open(filename, 'w') as f:
		f.write('# .PCD v0.7 - Point Cloud Data file format\n')
		f.write('VERSION 0.7\n')
		f.write('FIELDS x y z rgb Type idRegion\n')
		f.write('SIZE 4 4 4 4 4 4\n')
		f.write('TYPE F F F F U I\n')
		f.write('COUNT 1 1 1 1 1 1\n')
		f.write('WIDTH '+str(points.shape[1])+'\n')
		f.write('HEIGHT '+str(points.shape[0])+'\n')
		f.write('VIEWPOINT ')
		np.savetxt(f,transform.get_translation().reshape([1,3]),'%.5f',newline='')
		quaternion=np.array([1,0,0,0])# could use the thirdparty module transomartions.py by christoph gohlke
		f.write(' ')
		np.savetxt(f,quaternion.reshape(1,4),'%.5f',newline='')
		f.write('\n')
		f.write('POINTS '+str(points.shape[0]*points.shape[1])+'\n')
		
		for  key, value in idlabelToMaterial.iteritems():
			f.write('# material '+str(key)+' = '+value+'\n')
		f.write('DATA ascii\n')
		from struct import pack,unpack
		for i in xrange(points.shape[0]):
			for j in xrange(points.shape[1]):
				p=points[i,j]
				idpoly=idpolys[i,j]
				label=polygons[idpoly].label
				material=idlabelToMaterial[label]
				color=(labelColors[label]*255).astype(int)
				#color=[0,0,0]
				rgb_int = (color[0] << 16) | (color[1] << 8) | (color[2])
				rgb_string= "%.8e"%unpack("f",pack("I", rgb_int ))[0]# equivalent of c *reinterpret_cast<float*>

				rgb_int2=unpack('I',pack('f',float(rgb_string)))[0] # tha does not seem to work , as i do not get the right colors when using pcd_viewer
				assert(rgb_int==rgb_int2)
				color=[(rgb_int2>>16)& 0x0000ff,(rgb_int2>>8)& 0x0000ff,(rgb_int2)& 0x0000ff]
				f.write('%.7f'%p[0]+' '+'%.7f'%p[1]+' '+'%.7f'%p[2]+' '+rgb_string+' '+str(label)+' '+str(idpoly)+'\n')
				

def loadPCD(filename):
	header_dict=dict()
	with open(filename, 'r') as f:
		while True:
			line=f.readline()			
			line = line.rstrip('\n')	
			t=line.split(' ')
			if t[0][0]=='#':
				continue
			if t[0]!='DATA':
				header_dict[t[0]]=t[1:]
			else :
				break
		#Data=numpy.empty((header_dict['WIDTH'],header_dict['HEIGHT']),dtype=float)
		nbPoints=int(header_dict['POINTS'][0])
		DataArray=np.fromfile(f,  sep=' ',count=-1).reshape(nbPoints,-1)
		
		
		Data=dict()
		nbFields=len(header_dict['FIELDS'])
		for i,field,type,size in zip(range(nbFields),header_dict['FIELDS'],header_dict['TYPE'],header_dict['SIZE']):
			if type=='F':
				if size=='4':
					py_type=np.float32
				else:
					print 'not coded yet'				
			elif  type=='U':
				if size=='4':
					py_type=np.uint32
				else:
					print 'not coded yet'
			elif  type=='I':
				if size=='4':
					py_type=np.int32
				else:
					print 'not coded yet'				
			Data[field]=DataArray[:,i].astype(py_type)
			
		points=np.column_stack ((Data['x'],Data['y'],Data['z']))
		
		colors=np.empty((nbPoints,3),dtype=np.uint8)
		from struct import pack,unpack
		for i,color_float in enumerate(Data['rgb']):
			rgb_int=unpack('I',pack('f',color_float))[0] # tha does not seem to work , as i do not get the right colors when using pcd_viewer
			colors[i,:]=[(rgb_int>>16)& 0x0000ff,(rgb_int>>8)& 0x0000ff,(rgb_int)& 0x0000ff]		
		return points,colors, Data

		
if __name__ == "__main__":		
	points2,colors, transform=loadPCD('scan.pcd')