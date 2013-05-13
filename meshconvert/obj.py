#! /usr/bin/env python

# OBJ file format.  See http://www.fileformat.info/format/wavefrontobj/
# At the moment only v and f keywords are supported

import generic
import os

modeR = 'r'
modeW = 'w'

class reader(generic.reader):
	indexed = True

	def readNode(self):
		"Gets next node."
		nodeCounter = 0
		try:
			while True:
				line = self.getline()
				while line.endswith("\\"):
					# Remove backslash and concatenate with next line
					line = line[:-1] + self.getline()
				if line.startswith("v "):
					coord = line.split()
					coord.pop(0)
					nodeCounter += 1
					yield generic.node(coord[0], coord[1], coord[2], label=str(nodeCounter))
		except IOError:
			return
	def readMaterials(self):
		# look for the line starting with mtllib 
		self.f.seek(0)
		try:
			while True:
				line = self.getline()	
				if line.startswith("mtllib"):
								
					materialsFileName=line[6:].strip()	
					materialsFileName=os.path.join(os.path.dirname(self.f.name),materialsFileName)
					break
		except IOError:
			return						
			
		
			
		self.materialsDict={}
		material_name=''
		try:
			with open(materialsFileName,'r') as fm:
				       
				
					for line in fm:
						line.strip()					
						
						
						if line.startswith("#"):
							pass
						elif line.startswith("newmtl"):
							fields = line.split()
							fields.pop(0)
							
							if material_name!='':
								self.materialsDict[material_name]=material						
							material_name=fields[0]
							if self.materialsDict.has_key(material_name):
								print "material "+material_name+" already defined"
								raise
							material={}
							material['id']=len(self.materialsDict)
							
							
						else :	
							fields = line.split()
							attrname=fields.pop(0)	
							if attrname in ['Kd','Ka','Ks','Tr','d','D']:
								material[attrname]=[float(f) for f in fields]
							elif attrname in ['Ns']:      
								material[attrname]=[int(f) for f in fields]			
					self.materialsDict[material_name]=material		
		except IOError:
			return	

	def readElementIndexed(self):
		"Gets next element"
		self.f.seek(0)
		elementCounter = 0
		nodeCounter = 0
		self.materialsDict={}	
		materialId=0
		groupId=-1
		self.groupNames=[]
		if len(self.materialsDict)==0:
			self.readMaterials()
		
		try:
			while True:
				line = self.getline()
				while line.endswith("\\"):
					# Remove backslash and concatenate with next line
					line = line[:-1] + self.getline()
				if line.startswith("v "):
					nodeCounter += 1	
					
				elif line.startswith("f "):
					fields = line.split()
					fields.pop(0)
					elementCounter += 1					
					# in some obj faces are defined as -70//-70 -69//-69 -62//-62 
					cleanedFields=[]
					for f in fields: 
						f=f.split('/')[0]
						if f[0]=='-':
							f=str(nodeCounter+int(f)+1)
						cleanedFields.append(f)
					
					yield generic.indexedElement("Tri3", cleanedFields, label=str(elementCounter),materialId=materialId,groupId=groupId)
				elif line.startswith("g"):					
					groupId+=1
					self.groupNames.append(line[2:].strip())
				elif line.startswith("usemtl"):
					fields = line.split()					
					materialStr=fields[1]	
					if materialStr!='(null)':
						if not(self.materialsDict.has_key(materialStr)):	# add this material						
							self.materialsDict[materialStr]={'id':len(self.materialsDict),'Kd':[1,1,1]}
							print 'material '+materialStr+ ' not found in the materials file'
						materialId=self.materialsDict[materialStr]['id']
						
					else:
						materialId=0
		except IOError:
			return

def writer(file, reader):
	"Reads mesh from a reader and write it into an OBJ file"
	if not reader.indexed:
		reader = generic.soup2indexed(reader)

	nodeIndices = {}
	nodes = reader.readNode()
	nodeCounter = 0
	try:
		while True:
			n = nodes.next()
			nodeCounter += 1
			nodeIndices[n.label] = str(nodeCounter)
			file.write("v "+n.x+" "+n.y+" "+n.z+"\n")
	except StopIteration:
		pass

	elements = reader.readElementIndexed()
	elementCounter = 0
	try:
		while True:
			e = elements.next()
			elementCounter += 1
			file.write("f "+" ".join([nodeIndices[i] for i in e.list])+"\n")
	except StopIteration:
		pass

