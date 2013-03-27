#! /usr/bin/env python

# I-Deas Universal file format.  References?

import re
import logging
import generic

modeR = 'r'
modeW = 'w'

unv2fem = { "91": "Tri3", "94": "Quad4" }
fem2unv = {}
for k, v in unv2fem.items():
	fem2unv[v] = k

class reader(generic.reader):
	indexed = True

	def __init__(self, file, *args, **kw):
		super(reader, self).__init__(file, *args, **kw)
		self.seen = {}

	def _goToNextMark(self):
		"Reads lines until next -1 mark"
		while True:
			line = self.getline()
			if (line == "    -1"):
				return

	def _section(self, number):
		"Finds a numbered section in file"
		if self.logger.isEnabledFor(logging.DEBUG):
			self.logger.debug("Searching for section number %s" % number)
		while True:
			self._goToNextMark()
			line = self.getline()
			if (line == "    -1"):
				#  Err, maybe we were into a section, read another line
				line = self.getline()
			line = line.strip()
			self.seen[line] = True
			if (line == number):
				if self.logger.isEnabledFor(logging.DEBUG):
					self.logger.debug("Section %s found" % number)
				return
			if self.logger.isEnabledFor(logging.DEBUG):
				self.logger.debug("Skip section number %s" % line)
			self._goToNextMark()

	def readNode(self):
		"Gets next node"
		self._section("2411")
		floatPattern = re.compile("[DE]")
		while True:
			line = self.getline()
			if (line == "    -1"):
				return
			fields = line.split()
			line = self.getline()
			line = re.sub(floatPattern, "e", line)
			coord = line.split()
			yield generic.node(coord[0], coord[1], coord[2], label=fields[0], color=fields[3])

	def readElementIndexed(self):
		"Gets next element."
		try:
			self._section("2412")
		except IOError:
			# EOF reached, reset file
			if "2412" not in self.seen:
				raise IOError, "Section %s not found" % "2412"
			self.f.seek(0)
			self._section("2412")

		while True:
			line = self.getline()
			if (line == "    -1"):
				return
			fields = line.split()
			line = self.getline()
			nodeList = line.split()
			yield generic.indexedElement(unv2fem[fields[1]], nodeList, label=fields[0], color=fields[4])

def normFloat(s):
	return ("%25.16e" % float(s)).replace("e", "D")

def writer(file, reader):
	"Reads mesh from a reader and write it into a UNV file"
	if not reader.indexed:
		reader = generic.soup2indexed(reader)
	file.write("""    -1
  2411
""")
	nodeIndices = {}
	nodes = reader.readNode()
	nodeCounter = 0
	try:
		while True:
			n = nodes.next()
			nodeCounter += 1
			file.write("%10s         1         1%10s\n" % (n.label, n.color))
			c = [normFloat(i) for i in [n.x, n.y, n.z]]
			file.write("".join(c)+"\n")
			nodeIndices[n.label] = str(nodeCounter)
	except StopIteration:
		pass
	file.write("""    -1
    -1
  2412
""")
	elements = reader.readElementIndexed()
	elementCounter = 0
	try:
		while True:
			e = elements.next()
			file.write("%10s%10s         1         1         1%10d\n" % (e.label, fem2unv[e.type], len(e.list)))
			file.write("".join(["%10s" % (nodeIndices[i]) for i in e.list])+"\n")
			elementCounter += 1
	except StopIteration:
		pass
	file.write("    -1\n")

