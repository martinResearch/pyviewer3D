#! /usr/bin/env python

# Mesh file format for medit.  See file format description (French only) in
#  http://www.ann.jussieu.fr/~frey/logiciels/Docmedit.dir/Fichiers/formatmesh.pdf

import tempfile
import logging
import generic

modeR = 'r'
modeW = 'w'

class reader(generic.reader):
	indexed = True

	def _section(self, label):
		"Finds a labeled section in file"
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Searching for section labeled '%s'" % label)
		while True:
			line = self.getline()
			if (line == label):
				return

	def readNode(self):
		"Gets next node"
		self._section("Vertices")
		number = int(self.getline())
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Mesh contains %d vertices" % number)
		for i in xrange(number):
			line = self.getline()
			coord = line.split()
			yield generic.node(coord[0], coord[1], coord[2], label=str(i+1), color=coord[3])

	def readElementIndexed(self):
		"Gets next element."
		try:
			self._section("Triangles")
		except IOError:
			# EOF reached, reset file
			self.f.seek(0)
			self._section("Triangles")

		number = int(self.getline())
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Mesh contains %d triangles" % number)
		for i in xrange(number):
			line = self.getline()
			nodeList = line.split()
			last = nodeList.pop()
			yield generic.indexedElement("Tri3", nodeList, label=str(i+1), color=last)

def writer(file, reader):
	"Reads mesh from a reader and write it into a MESH file"
	if not reader.indexed:
		reader = generic.soup2indexed(reader)

	try:
		name = file.name
	except AttributeError:
		name = ""

	tempFiles = [tempfile.TemporaryFile(mode='w+') for i in range(5)]
	tempFiles[0].write("""
MeshVersionFormatted 1

Dimension
3

Geometry
"""+'"'+name+'"'+"""

""")

	nodeIndices = {}
	nodes = reader.readNode()
	nodeCounter = 0
	try:
		while True:
			n = nodes.next()
			nodeCounter += 1
			nodeIndices[n.label] = str(nodeCounter)
			tempFiles[2].write(n.x+" "+n.y+" "+n.z+" "+n.color+"\n")
	except StopIteration:
		pass

	tempFiles[1].write("\nVertices\n"+str(nodeCounter)+"\n")

	elements = reader.readElementIndexed()
	elementCounter = 0
	try:
		while True:
			e = elements.next()
			assert e.type == "Tri3"
			tempFiles[4].write(" ".join([nodeIndices[i] for i in e.list])+" "+e.color+"\n")
			elementCounter += 1
	except StopIteration:
		pass

	tempFiles[4].write("""
SubDomainFromMesh
1
3 1 1 1

End
""")

	tempFiles[3].write("\nTriangles\n"+str(elementCounter)+"\n")

	for f in tempFiles:
		f.seek(0)
		while True:
			line = f.readline()
			if line == "":
				break
			file.write(line)
		f.close

