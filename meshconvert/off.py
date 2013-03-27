#! /usr/bin/env python

# OFF file format  http://shape.cs.princeton.edu/benchmark/documentation/off_format.html

import generic
import string
import tempfile
import logging

modeR = 'r'
modeW = 'w'

class reader(generic.reader):
	indexed = True

	def __init__(self, file, *args, **kw):
		"Opens OFF file for reading"
		super(reader, self).__init__(file, *args, **kw)
		#  Read number of nodes and elements
		line = self.getline()
		assert line == "OFF"
		line = self.getline()
		# Ignore number of edges
		fields = line.split()
		self.nrNodes = int(fields[0])
		self.nrElements = int(fields[1])
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Mesh contains %d vertices and %d elements" % (self.nrNodes, self.nrElements))

	def readNode(self):
		"Gets next node"
		for i in xrange(self.nrNodes):
			line = self.getline()
			coord = line.split()
			yield generic.node(coord[0], coord[1], coord[2], label=str(i+1))

	def readElementIndexed(self):
		"Gets next element"
		for i in xrange(self.nrElements):
			line = self.getline()
			fields = line.split()
			assert fields[0] == '3'
			fields.pop(0)
			nodeList = [str(string.atoi(k)+1) for k in fields]
			yield generic.indexedElement("Tri3", nodeList, label=str(i+1))

def writer(file, reader):
	"Reads mesh from a reader and write it into a OFF file"
	if not reader.indexed:
		reader = generic.soup2indexed(reader)

	tempFiles = [tempfile.TemporaryFile(mode='w+') for i in range(2)]
	tempFiles[0].write("OFF\n")

	nodeIndices = {}
	nodes = reader.readNode()
	nodeCounter = 0
	try:
		while True:
			n = nodes.next()
			nodeIndices[n.label] = str(nodeCounter)
			tempFiles[1].write(n.x+" "+n.y+" "+n.z+"\n")
			nodeCounter += 1
	except StopIteration:
		pass

	tempFiles[0].write(str(nodeCounter)+" ")

	elements = reader.readElementIndexed()
	elementCounter = 0
	try:
		while True:
			e = elements.next()
			tempFiles[1].write(str(len(e.list))+" "+" ".join([nodeIndices[i] for i in e.list])+"\n")
			elementCounter += 1
	except StopIteration:
		pass

	tempFiles[0].write(str(elementCounter)+" 0\n")

	for f in tempFiles:
		f.seek(0)
		while True:
			line = f.readline()
			if line == "":
				break
			file.write(line)
		f.close

