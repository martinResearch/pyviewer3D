#! /usr/bin/env python

# Triangle soup, as used by JCAE

import generic
import struct

modeR = 'rb'
modeW = 'wb'

def writer(file, reader, string=False):
	"Reads mesh from a reader and writes it into a binary triangle soup file"

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
		try:
			while True:
				e = elements.next()
				assert e.type == "Tri3"
			        [file.write(struct.pack(">d", nodeCoord[i])) for i in e.list]
				file.write(struct.pack(">2i", int(e.color), 0))
				elementCounter += 1
		except StopIteration:
			pass
	else:
		elements = reader.readElement()
		try:
			while True:
				e = elements.next()
				assert e.type == "Tri3"
			        [[file.write(struct.pack(">d", float(j))) for j in i] for i in e.list]
				file.write(struct.pack(">2i", 0, 0))
		except StopIteration:
			pass

