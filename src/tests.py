#!/usr/bin/env python


def test_lib_component():
	library_Component = Kicad_Library_Component("Test", "T1")

	rectangle = Kicad_Rectangle(0, -20, 20, 0)
	print rectangle.show()
	
	
	poly = Kicad_Poly()
	poly.add_segment(100, 200)
	poly.add_segment(110, 210)		
	print poly.show()
	library_Component.addDraw(poly)
	print "-------------------"
	
	poly = Kicad_Poly()
	poly.add_segment(300, 400)
	poly.add_segment(330, 440)		
	print poly.show()
	library_Component.addDraw(poly)
	print "-------------------"
	

	
	to_write = library_Component.show()
	for line in to_write:
		print line,

		