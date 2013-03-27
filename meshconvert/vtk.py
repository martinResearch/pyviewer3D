#! /usr/bin/env python

# VTK polydata file format.  References?

import tempfile
import struct
import logging

modeR = 'rb'
modeW = 'wb'

def reader(file):
	raise ValueError, "Module "+`__name__`+" does not define a reader method"

def writer(file, reader):
	if not reader.indexed:
		reader = generic.soup2indexed(reader)
	logger=logging.getLogger(__name__)
	#logging.basicConfig(level=logging.DEBUG)

	tempFiles = [tempfile.TemporaryFile() for i in range(6)]
	nodeIndices = {}
	nodes = reader.readNode()
	nodeCounter = 0
	try:
		while True:
			n = nodes.next()
			tempFiles[2].write(struct.pack(">3d", float(n.x), float(n.y), float(n.z)))
			nodeIndices[n.label] = nodeCounter
			nodeCounter += 1
	except StopIteration:
		pass

	tempFiles[1].write(struct.pack(">I", nodeCounter*8*3))

	elements = reader.readElementIndexed()
	elementCounter = 0
	try:
		while True:
			e = elements.next()
			assert e.type == "Tri3"
			[tempFiles[4].write(struct.pack(">I", nodeIndices[i])) for i in e.list]
			elementCounter += 1
	except StopIteration:
		pass
	tempFiles[4].write(struct.pack(">I", elementCounter*4))
	for i in xrange(elementCounter):
		tempFiles[4].write(struct.pack(">I", (i+1)*3))

	tempFiles[3].write(struct.pack(">I", elementCounter*4*3))

	tempFiles[0].write("""<VTKFile type="PolyData" version="0.1" byte_order="BigEndian">
<PolyData>
<Piece NumberOfPoints="""+'"'+str(nodeCounter)+'" NumberOfPolys="'+str(elementCounter)+'"'+""">
<Points><DataArray type="Float64" NumberOfComponents="3" format="appended" offset="0"/></Points>
""")
	offset = 4+(nodeCounter*8*3)
	tempFiles[0].write('<Polys><DataArray type="Int32" Name="connectivity" format="appended" offset="'+str(offset)+'"/>\n')
	offset += 4+elementCounter*4*3
	tempFiles[0].write('<DataArray type="Int32" Name="offsets" format="appended" offset="'+str(offset)+'"/></Polys>\n')
	offset += 4+elementCounter*4
	tempFiles[0].write('</Piece></PolyData>\n')
	tempFiles[0].write('<AppendedData encoding="raw"> _')

	tempFiles[5].write('</AppendedData></VTKFile>\n')

	for f in tempFiles:
		f.seek(0)
		# TODO: This is a binary file, we should use a better alternative
		for line in f:
			file.write(line)
		f.close()

