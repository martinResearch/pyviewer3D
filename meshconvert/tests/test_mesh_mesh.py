#! /usr/bin/env python

import unittest
import os, sys
import StringIO

# Run tests against current sources
dirname = os.path.dirname(__file__)
if (dirname == ''):
	dirname = '.'
dirname = os.path.realpath(dirname)
parent = os.path.split(dirname)[0]
sys.path.insert(0, parent)

import mesh

class meshTest(unittest.TestCase):
	strTest1 = """
MeshVersionFormatted 1

Dimension
3

Geometry
""


Vertices
3
0 0 0 0
0 0 0 0
0 0 0 0

Triangles
1
1 2 3 1

SubDomainFromMesh
1
3 1 1 1

End
"""
	def test1(self):
		reader = mesh.reader(StringIO.StringIO(self.strTest1))
		outputString = StringIO.StringIO()
		mesh.writer(outputString, reader)
		res = outputString.getvalue()
		outputString.close()
		self.assertEquals(res, self.strTest1)

def test_suite():
	tests = [unittest.makeSuite(meshTest)]
	return unittest.TestSuite(tests)

if __name__ == '__main__':
	unittest.main(defaultTest='test_suite')

