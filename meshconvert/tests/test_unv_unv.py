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

import unv

class unvTest(unittest.TestCase):
	strTest1 = """    -1
  2411
         1         1         1         1
   0.0000000000000000D+00   0.0000000000000000D+00   0.0000000000000000D+00
         2         1         1         1
   0.0000000000000000D+00   0.0000000000000000D+00   0.0000000000000000D+00
         3         1         1         1
   0.0000000000000000D+00   0.0000000000000000D+00   0.0000000000000000D+00
    -1
    -1
  2412
         1        91         1         1         1         3
         1         2         3
    -1
"""
	def test1(self):
		reader = unv.reader(StringIO.StringIO(self.strTest1))
		outputString = StringIO.StringIO()
		unv.writer(outputString, reader)
		res = outputString.getvalue()
		outputString.close()
		self.assertEquals(res, self.strTest1)

def test_suite():
	tests = [unittest.makeSuite(unvTest)]
	return unittest.TestSuite(tests)

if __name__ == '__main__':
	unittest.main(defaultTest='test_suite')

