#! /usr/bin/env python

# STL file format  http://local.wasp.uwa.edu.au/~pbourke/dataformats/stl/

import generic

modeR = 'r'
modeW = 'w'

class reader(generic.reader):
	def readElement(self):
		"Gets next element."
		while True:
			line = self.getline().strip()
			if (line.startswith("solid")):
				break
		while True:
			line = self.getline().strip()
			if (line.startswith("endsolid")):
				return
			assert line.startswith("facet")
			line = self.getline().strip()
			assert line == "outer loop"
			coord = []
			for i in xrange(3):
				line = self.getline().strip()
				assert line.startswith("vertex ")
				nodeList = line.split()
				nodeList.pop(0)
				coord.append(nodeList)
			line = self.getline().strip()
			assert line == "endloop" or line == "end loop"
			line = self.getline().strip()
			assert line == "endfacet" or line == "end facet"
			yield generic.element("Tri3", coord)


def writer(file, reader):
	"Reads mesh from a reader and write it into a STL file"

	if reader.indexed:
		nodeCoord = {}
		nodes = reader.readNode()
		nodeCounter = 0
		try:
			while True:
				n = nodes.next()
				nodeCoord[n.label] = (n.x, n.y, n.z)
		except StopIteration:
			pass

		elements = reader.readElementIndexed()
		elementCounter = 0
		file.write("solid\n")
		try:
			while True:
				e = elements.next()
				assert e.type == "Tri3"
				file.write(" facet\n")
				file.write("  outer loop\n")
				for i in xrange(3):
					file.write("   vertex "+" ".join(nodeCoord[e.list[i]])+"\n")
				file.write("  endloop\n")
				file.write(" endfacet\n")
				elementCounter += 1
		except StopIteration:
			pass
		file.write("endsolid\n")
	else:
		elements = reader.readElement()
		file.write("solid\n")
		try:
			while True:
				e = elements.next()
				assert e.type == "Tri3"
				file.write(" facet\n")
				file.write("  outer loop\n")
				for i in xrange(3):
					file.write("   vertex "+" ".join(e.list[i])+"\n")
				file.write("  endloop\n")
				file.write(" endfacet\n")
		except StopIteration:
			pass
		file.write("endsolid\n")

