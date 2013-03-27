#! /usr/bin/env python

# Gridgen binary file format.  References?

import logging, struct
import generic

class reader(generic.reader):
	indexed = False

	def __init__(self, file):
		"Opens Gridgen binary file for reading"
		generic.reader.__init__(self, file)
		#  Skip header
		self.f.seek(84)
		#logging.basicConfig(level=logging.DEBUG)

	def readElement(self):
		"Gets next element"
		while True:
			buf = self.f.read(50)
			if (len(buf) == 0):
				break
			coord = []
			for i in range(3):
				coord.append([x for x in struct.unpack_from("3f", buf, (i+1)*12)])
			color = str(struct.unpack_from("h", buf, 48)[0])
			print color
			yield generic.element("Tri3", list=coord, color=color)

def writer(file, reader):
	raise ValueError, "Module "+`__name__`+" does not define a writer method"

