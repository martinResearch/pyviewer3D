#! /usr/bin/env python

# Gridgen ASCII file format.  References?

import logging, struct
import re
import generic

modeR = 'r'
modeW = 'w'

class reader(generic.reader):
	indexed = True

	def __init__(self, file):
		"Opens Gridgen file for reading"
		generic.reader.__init__(self, file)
		#  Read number of nodes and elements
		line = self.getline()
		line = self.getline()
		line = self.getline()
		fields = line.split()
		self.nrNodes = int(fields[4])
		self.nrElements = int(fields[5])
		self.counterNodes = 0
		self.counterElements = 0
		self.position = "start"
		line = self.getline()
		#logging.basicConfig(level=logging.DEBUG)

	def readNode(self):
		"Gets next node"
		if self.position != "start":
			self.logger.debug("Reset to node location")
			self.f.seek(0)
			for i in range(4):
				line = self.getline()
		self.position = "nodes"
		floatPattern = re.compile("[DE]")
		while self.counterNodes < self.nrNodes:
			line = self.getline()
			label = line.split()[1]
			line = self.getline()
			line = re.sub(floatPattern, "e", line)
			coord = struct.unpack("16s16s16s", line)
			line = self.getline()
			self.counterNodes += 1
			yield generic.node(coord[0], coord[1], coord[2], label=label)

	def readElementIndexed(self):
		"Gets next element"
		if self.position != "nodes":
			self.logger.warn("Rewind to element location")
			self.f.seek(0)
			for i in xrange(4+3*self.nrNodes):
				line = self.getline()
		self.position = "elements"
		while self.counterElements < self.nrElements:
			line = self.getline()
			label = line.split()[1]
			line = self.getline()
			color = line.split()[2]
			line = self.getline()
			nodeList = line.split()
			self.counterElements += 1
			yield generic.indexedElement("Tri3", nodeList, label=label, color=color)

def writer(file, reader):
	raise ValueError, "Module "+`__name__`+" does not define a writer method"

