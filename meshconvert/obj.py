#! /usr/bin/env python

# OBJ file format.  See http://www.fileformat.info/format/wavefrontobj/
# At the moment only v and f keywords are supported

import generic

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

	def readElementIndexed(self):
		"Gets next element"
		self.f.seek(0)
		elementCounter = 0
		try:
			while True:
				line = self.getline()
				while line.endswith("\\"):
					# Remove backslash and concatenate with next line
					line = line[:-1] + self.getline()
				if line.startswith("f "):
					fields = line.split()
					fields.pop(0)
					elementCounter += 1
					yield generic.indexedElement("Tri3", fields, label=str(elementCounter))
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

