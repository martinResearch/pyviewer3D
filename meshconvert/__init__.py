#! /usr/bin/env python

from optparse import OptionParser
import sys

formats = {
	(".unv",): "unv",
	(".mesh", ".msh"): "mesh",
	(".grd",): "gridgen",
	(".grb",): "gridgenb",
	(".vtp",): "vtk",
	(".ply",): "ply",
	(".off",): "off",
	(".stl",): "stl",
	(".obj",): "obj",
	(".soup",): "soupb",
}

def getFormat(file, flag):
	try:
		suffix = file[file.rindex("."):].lower()
		for list, format in formats.iteritems():
			if suffix in list:
				return format
		raise ValueError
	except ValueError:
		raise ValueError, "Cannot guess file format for "+file+", please specify one with "+flag+" flag"

def cli(argv, prog=None):
	inputFormat = None
	outputFormat = None
	if prog is None:
		prog = "meshconvert"
	usage = "usage: %prog [options] INPUTFILE OUTPUTFILE"
	parser = OptionParser(usage=usage, prog=prog)
	parser.add_option("-I", "--input-format", metavar="STRING", action="store", type="string", dest="inputFormat", help="set input format")
	parser.add_option("-O", "--output-format", metavar="STRING", action="store", type="string", dest="outputFormat", help="set output format")
	(options, args) = parser.parse_args(args=argv)
	if (len(args) != 2):
		parser.error("incorrect number of arguments")
	inputFile, outputFile = args

	inputFormat = options.inputFormat and options.inputFormat or getFormat(inputFile, "-I")
	outputFormat = options.outputFormat and options.outputFormat or getFormat(outputFile, "-O")

	try:
		inputModule =  __import__("meshconvert."+inputFormat, globals(),  locals(), [""])
	except ImportError:
		raise ValueError, "Unknown mesh format: "+inputFormat
	try:
		outputModule =  __import__("meshconvert."+outputFormat, globals(),  locals(), [""])
	except ImportError:
		raise ValueError, "Unknown mesh format: "+outputFormat
	outputModule.writer(open(outputFile, outputModule.modeW), inputModule.reader(open(inputFile, inputModule.modeR)))

if __name__ == "__main__":
	cli(sys.argv[1:], prog=sys.argv[0])

