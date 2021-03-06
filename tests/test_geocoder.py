#!/usr/local/opt/python/bin/python2.7

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import pytest
import geocoder
import SGC_output
import subprocess

version = "SpeciesGeoCoder 0.9.7\n"

class TestParser:

	def test_version(self, capsys):
		with pytest.raises(SystemExit):
			args = geocoder.parse_args(['--version'])
		out, err = capsys.readouterr()
		assert err == version

class TestClass:
	
	def setup_args(self):
#		return geocoder.parse_args(['-p', 'example_data/polygons.txt', '-l', 'example_data/localities.csv'])
		return geocoder.parse_args(['-p', 'example_data/polygons.txt', '-l', 'example_data/localities.csv', '-t', 'example_data/*.tif'])

	def setup_args2(self):
		return geocoder.parse_args(['-p', 'example_data/polygons.txt', '-g', 'example_data/gbif_Ivesia_localities.txt'])

	def setup_args3(self):
		# Coordinate columns in the "wrong" order.
		return geocoder.parse_args(['-p', 'example_data/polygons.txt', '-l', 'tests/localities_wrong_coordinate-order.csv'])

class TestClassTextPolygons(TestClass):
	# Test the class TextPolygons and at the same time the polygon file

	def setup_TestTextPolygons(self):
		self.args = self.setup_args()
		self.TestTextPolygons = geocoder.TextPolygons(self.args)
		self.polygon = list(self.TestTextPolygons.getPolygons())

	def loop_over_polygons(self, position):
		for item in self.polygon:
			nr = 0
			assert self.polygon[nr][position] == SGC_output.polygons[nr][position]
			nr += 1

	def test_number_of_polygons(self):
		# Test number of polygons in input file
		self.setup_TestTextPolygons()
		assert len(self.polygon) == 8
		
	def test_polygonNames(self):
		# Test names of polygons
		self.setup_TestTextPolygons()
		# Test first list that only contains the polygon names
		assert self.TestTextPolygons.polygonNames == SGC_output.polygonNames

		self.loop_over_polygons(position=0)

	def test_polygons(self):
		# Test the polygons
		self.setup_TestTextPolygons()
		self.loop_over_polygons(position=1)

	def test_low(self):
		# Test the low value of the elevation range
		self.setup_TestTextPolygons()
		self.loop_over_polygons(position=2)

	def test_high(self):
		# Test the high value of the elevation range
		self.setup_TestTextPolygons()
		self.loop_over_polygons(position=3)
	
	def test_setPolygonName(self):
		# Again test the list that only contains the names of the polygons
		self.setup_TestTextPolygons()
		self.TestTextPolygons.setPolygonName('New_Polygon')
		assert self.TestTextPolygons.polygonNames == SGC_output.modified_polygonNames

	def test_getPolygonNames(self):
		self.setup_TestTextPolygons()
		assert self.TestTextPolygons.getPolygonNames() == SGC_output.polygonNames

class TestClassTextLocalities(TestClass):
	
	def setup_TestTextLocalities(self):
		self.args = self.setup_args()
		self.TestTextLocalities = geocoder.TextLocalities(self.args, 'example_data/localities.csv')
	def setup_TestTextLocalities_wrong_coordinate_order(self):
		# Using wrong coordinate culomn order
		self.args3 = self.setup_args3()
		self.TestTextLocalities3 = geocoder.TextLocalities(self.args3, 'example_data/localities.csv')
	
	def test_speciesNames(self):
# Perhaps redundant
		# Test species names
        	self.setup_TestTextLocalities()
        	# Test first list that only contains the species names
        	assert self.TestTextLocalities.speciesNames == SGC_output.speciesNames

	def test_getLocalities(self):
		self.setup_TestTextLocalities()
		assert list(self.TestTextLocalities.getLocalities()) == SGC_output.localities

	def test_getLocalities_wrong_coordinate_order(self):
		self.setup_TestTextLocalities_wrong_coordinate_order()
		assert list(self.TestTextLocalities3.getLocalities()) == SGC_output.localities

	def test_getCoOrder(self):
		self.setup_TestTextLocalities()
		assert self.TestTextLocalities.getCoOrder() == 'lat-long'

	def test_setSpeciesNames(self):
		self.setup_TestTextLocalities()
		self.TestTextLocalities.setSpeciesName('New Species')
		assert self.TestTextLocalities.speciesNames == SGC_output.modified_speciesNames

	def test_getSpeciesNames(self):
		self.setup_TestTextLocalities()
		assert self.TestTextLocalities.getSpeciesNames() == SGC_output.speciesNames

	def test_getLocalityFileName(self):
		self.setup_TestTextLocalities()
		assert self.TestTextLocalities.getLocalityFileName() == 'example_data/localities.csv'
	
	def test_getBinomialName(self):
		self.setup_TestTextLocalities()
		assert self.TestTextLocalities.getBinomialName('New species name') == 'New species'
		assert self.TestTextLocalities.getBinomialName('New species with name') == 'New species'
# Perhaps something to implement
#		assert self.TestTextLocalities.getBinomialName('New_species + name') == 'New species'

	def test_getNrLocalities(self):
		self.setup_TestTextLocalities()
		assert self.TestTextLocalities.getNrLocalities() == 571


class TestGbifLocalities(TestClass):

	def setup_TestGbifLocalities(self):
		self.args = self.setup_args2()
		self.TestGbifLocalities = geocoder.GbifLocalities(self.args)

	def test_getLocalities(self):
		self.setup_TestGbifLocalities()
		assert list(self.TestGbifLocalities.getLocalities()) == SGC_output.gbifLocalities

	def test_setSpeciesNames(self):
		pass

	def test_getSpeciesNames(self):
		self.setup_TestGbifLocalities()
#		print self.TestGbifLocalities.getSpeciesNames()
		assert self.TestGbifLocalities.getSpeciesNames() == SGC_output.gbifSpeciesNames

	def test_getgbifFile(self):
		self.setup_TestGbifLocalities()
		assert self.TestGbifLocalities.getgbifFile() == 'example_data/gbif_Ivesia_localities.txt'

	def test_getNrLocalities(self):
		self.setup_TestGbifLocalities()
		assert self.TestGbifLocalities.getNrLocalities() == 3458


class TestPointInPolygon(TestClass):

	def setup_PipTest(self):
		self.poly = ['-118.005656529728995 45.98799579322525233', '-115.69029553728493909 42.88839962592111021', '-113.48696814124947707 42.88839962592111021', '-113.82306893047521612 47.29505441799205556', '-115.31685021592299734 49.16228102480177853', '-118.37910185109095096 49.08759196052939444', '-118.0430010618651977 48.04194506071594617', '-116.58656430855361918 47.33239895012825116', '-118.005656529728995 45.98799579322525233']

	def test_False(self):
		self.setup_PipTest()
		x = -120.42
		y = 39.48
		locality = ['Specie name', y, x]
#		print list(geocoder.pointInPolygon(poly, x, y))
		assert geocoder.pointInPolygon(self.poly, locality) == False
	
	def test_True1(self):
		self.setup_PipTest()
		x = -117.0
		y = 46.0
		locality = ['Specie name', y, x]
		assert geocoder.pointInPolygon(self.poly, locality) == True

	def test_True2(self):
		self.setup_PipTest()
		x = -117.1111111111111111111111111111111111111111111111
		y = 46.1111111111111111111111111111111111111111111111
		locality = ['Specie name', y, x]
		assert geocoder.pointInPolygon(self.poly, locality) == True

	def test_OnEdge(self):
		self.setup_PipTest()
		x = -118.005656529728995
		y = 45.98799579322525233
		locality = ['Specie name', y, x]
		assert geocoder.pointInPolygon(self.poly, locality) == False

	def test_NonFloat(self):
		self.setup_PipTest()
		x = 0
		y = 1
		locality = ['Specie name', y, x]
		assert geocoder.pointInPolygon(self.poly, locality) == False

	def test_NonNumber(self):
		self.setup_PipTest()
		x = 'yes'
		y = 'no'
		locality = ['Specie name', y, x]
		assert geocoder.pointInPolygon(self.poly, locality) == False

#	def test_InputData(self):		
#		self.setup_args()
#		pass
# Perhaps later


class TestelevationTest:

	def setup_elevationTest(self):
		self.lat = 0 
		self.lon = 0
		self.polygon = ('Test Polygon', ['1.0 0.0', '1.0 1.0', '0.0 1.0', '0.0 0.0'], None, None)
		self.polygons = SGC_output.polygons
#		self.index = {'foo.tif': [17.9, 19.0, 56.9, 58.0]}
		self.index = {'foo.tif': [0.0, 1.0, 0.0, 1.0]}

	def test_NoElevation(self):
		self.setup_elevationTest()
		assert geocoder.elevationTest(self.lat, self.lon, self.polygon, self.index) == True

	def test_CorrectFile(self):
		pass		

	def test_NotCorrectFile(self):
		# [ Warning ] No elevation data available for locality -120.42, 39.48
		pass


class TestPrintProgress:
	
	def setup_printProgress(self):
		pass


class TestMain:

	def setup_main(self):
		pass
		

class TestResult(TestClass):
	
	def test_RegularOutput(self, capsys):
		# Test the regular output using locality data in csv format and polygons in text format.
		myProcess = subprocess.Popen('speciesgeocoder -l example_data/localities.csv -p example_data/polygons.txt',shell=True, stdout=subprocess.PIPE)
		nexus = open('tests/SGC_output.NEXUS', 'r')
		assert myProcess.stdout.readlines() == nexus.readlines()

	def test_RegularOutput2(self, capsys):
		# Test the regular output using locality data in csv 
		# format with the lat. long. columns in the "wrong" 
		# order and polygons in text format.
		myProcess2 = subprocess.Popen('speciesgeocoder -l tests/localities_wrong_coordinate-order.csv -p example_data/polygons.txt',shell=True, stdout=subprocess.PIPE)
		nexus2 = open('tests/SGC_output.NEXUS', 'r')
		assert myProcess2.stdout.readlines() == nexus2.readlines()

	def test_ElevationOutput(self):
		# Same as test_RegularOutput() but also using elevation data.
		myElevationProcess = subprocess.Popen('speciesgeocoder -l example_data/localities.csv -p example_data/polygons.txt -t example_data/*.tif',shell=True, stdout=subprocess.PIPE)
		elevationNexus = open('tests/SGC_elevation_output.NEXUS', 'r')
		assert myElevationProcess.stdout.readlines() == elevationNexus.readlines()
	
	def testRegularGbifOutput(self):
		# Test the regular output using Gbif locality data and polygons in text format.
		myProcess = subprocess.Popen('speciesgeocoder -g example_data/gbif_Ivesia_localities.txt -p example_data/polygons.txt',shell=True, stdout=subprocess.PIPE)
		nexus = open('tests/SGE_Gbif-output.NEXUS', 'r')
		assert myProcess.stdout.readlines() == nexus.readlines()

	def testRegularShapePolygonOutput(self):
		# Test the regular output using locality data in csv
		# and a polygon in Shape format.
		myProcess = subprocess.Popen('speciesgeocoder -l example_data/localities.csv --p_shape tests/SierraNevada',shell=True, stdout=subprocess.PIPE)
		shapeOutput = open('tests/SGE_Shape-output.NEXUS', 'r')
		assert myProcess.stdout.readlines() == shapeOutput.readlines()


class TestoutputFile():
	
	def test_withOutputFile(self):
		pass



