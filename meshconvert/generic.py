#! /usr/bin/env python

import logging

logger=logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)

modeR = 'r'
modeW = 'w'

class reader(object):
	indexed = False

	def __init__(self, file):
		"Opens file for reading"
		self.f = file
		self.lineno = 0
		self.logger=logging.getLogger(__name__)

	def getline(self):
		"Reads a line from file.  Raises IOError at EOF."
		self.lineno += 1
		line = self.f.readline()
		if (line == ""):
			raise IOError
		line = line.rstrip()
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Reading line %d: %s" % (self.lineno, line))
		return line

	def rewind(self):
		self.f.seek(0)
		self.lineno = 0

class node(object):
	def __init__(self, x, y, z, label='1', color='0'):
		"Mesh node"
		self.x = x
		self.y = y
		self.z = z
		self.label = label
		self.color = color
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug("found node label=%s (%s,%s,%s) color=%s" % (self.label, self.x, self.y, self.z, self.color))

	def __hash__(self):
		return hash(self.x) + hash(self.y) + hash(self.z)

	def __eq__(self, that):
		return self.x == that.x and self.y == that.y and self.z == that.z and self.label == that.label and self.color == that.color

class indexedElement(object):
	def __init__(self, type, list, label='1', color='0'):
		"Indexed mesh element.  Vertex indices start from 1"
		self.type = type
		self.list = list
		self.label = label
		self.color = color
		if logger.isEnabledFor(logging.DEBUG):
			logger.debug("found element label=%s (%s) color=%s" % (self.label, ",".join(self.list), self.color))

class element(object):
	def __init__(self, type, list, color='0'):
		"Mesh element"
		self.type = type
		self.list = list
		self.color = color

class soup2indexed(object):
	def __init__(self, soupReader):
		self.nodes = {}
		self.elements = soupReader.readElement()
		counter = 0
		try:
			while True:
				e = self.elements.next()
				for i in xrange(3):
					coord = e.list[i]
					n = node(coord[0], coord[1], coord[2])
					if (self.nodes.has_key(n)):
						continue
					counter += 1
					self.nodes[n] = counter
		except StopIteration:
			pass
		soupReader.rewind()
		self.elements = soupReader.readElement()

	def readNode(self):
		"Gets next node"
		for n in self.nodes:
			yield node(n.x, n.y, n.z, str(self.nodes[n]))

	def readElementIndexed(self):
		"Gets next element."
		try:
			while True:
				e = self.elements.next()
				list = []
				for i in xrange(3):
					coord = e.list[i]
					n = node(coord[0], coord[1], coord[2])
					list.append(str(self.nodes[n]))
				yield indexedElement(e.type, list)
		except StopIteration:
			pass

