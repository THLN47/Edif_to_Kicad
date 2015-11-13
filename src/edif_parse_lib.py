#!/usr/bin/env python

from kicad_lib import *

from Edif_parser_mod import *

def extract_connections(library_Component, port_impl_list, port_list):
	
	for port_impl in port_impl_list:
			
		i_name = port_impl.get_object("name")					
		if (i_name!=None):
			port_impl_p_name = i_name.get_param(0)
			
			if (port_impl_p_name!=None):
				#print "port_impl_p_name =", port_impl_p_name
				
				pin_name, pin_type, pin_number = extract_pin_parameters(port_impl_p_name, port_list)
				#print pin_name, pin_type, pin_number
				
				if (pin_number!=None):
					connection = Kicad_Connection(pin_number, pin_name)
				
					dot_pt = port_impl.get_object("connectLocation.figure.dot.pt")								
					if (dot_pt!=None):
						dot_x, dot_y = convert_kicad_coor( extract_edif_pt(dot_pt) )
							
					ptl_pin = port_impl.get_object("figure.path.pointList")
					if (ptl_pin!=None):
						x1, y1 = convert_kicad_coor( extract_edif_pt(ptl_pin.get_param(0)) )
						x2, y2 = convert_kicad_coor( extract_edif_pt(ptl_pin.get_param(1)) )
						# x1 = dot_x
						# y1 = dot_y							
						connection.set_pin(x1, y1, x2, y2)
					
					library_Component.addConnection(connection)				
	return

def extract_point_list(library_Component, point_list):
	for ptl in point_list:								
		poly = Kicad_Poly()
		pts = search_edif_objects(ptl, "pt")	
		for pt in pts:
			x, y = convert_kicad_coor( extract_edif_pt(pt) )					
			poly.add_segment(x, y)
		library_Component.addDraw(poly)		
	return
	
def extract_path(library_Component, path_list):
	for path in path_list:
		point_list = search_edif_objects(path, "pointList")														
		extract_point_list(library_Component, point_list)
	return
		
#def extract_rectangle(library_Component, )		
		
def extract_drawing(library_Component, figure_list):						
	for figure in figure_list:
		p1 = extract_edif_str_param(figure, 0)
		if (p1!=None):
			#print "figure : "+p1[1] # PARTBODY
			#if (p1[1]=="PARTBODY"):
			
			
			path_list = search_edif_objects(figure, "path")
			extract_path(library_Component, path_list)

		point_list = figure.get_object("polygon.pointList") 
		if (point_list!=None):
			extract_point_list(library_Component, [point_list] )			
			
		rectangle = figure.get_object("rectangle")
		if (rectangle!=None):			
			x1, y1 = convert_kicad_coor( extract_edif_pt(rectangle.get_param(0)) )
			x2, y2 = convert_kicad_coor( extract_edif_pt(rectangle.get_param(1)) )
			rectangle = Kicad_Rectangle(x1, y1, x2, y2)			
			library_Component.addDraw(rectangle)
		
		circle = figure.get_object("circle")
		if (circle!=None):
			x1, y1 = convert_kicad_coor( extract_edif_pt(circle.get_param(0)))
			x2, y2 = convert_kicad_coor( extract_edif_pt(circle.get_param(1)))
			circle = Kicad_Circle(x1, y1, x2, y2)
			library_Component.addDraw(circle)
					
	return
	
	
def extract_pin_parameters(port_impl_p_name, port_list):

	pin_name = None
	pin_type = None
	pin_number = None
		
	for port in port_list:
	
		if ( extract_edif_str_param(port, 0)[0]==port_impl_p_name):
			#print port_impl_p_name, "found"
			properties = search_edif_objects(port, "property")
			
			for property in properties:
				p1_name = remove_quote( extract_edif_str_param(property, 0)[1] )
				string = remove_quote( property.get_object("string").get_param(0) ) 
				#print p1_name, ":", string
								
				if (p1_name=="Name"):
					pin_name = string								
				elif (p1_name=="Type"):
					pin_type = string
				elif (p1_name=="PackagePortNumbers"):
					pin_number = string
			
	return [pin_name, pin_type, pin_number]	

	
	
def extract_kicad_component_library(edif_cell):
	cell_name = extract_edif_str_param(edif_cell, 0)
	#cell_name = cell.get_param(0)
	#print cell_name
	view = edif_cell.get_object("view")
	view_name = extract_edif_str_param(view, 0)
	
	#print view_name[0], view_name[0]
	
	library_Component = Kicad_Library_Component(cell_name[0])
	
	library_Component.addAlias(view_name[0])
	
	
	contents =  view.get_object("contents") 
	if (contents!=None):		
		figure_list = search_edif_objects(contents, "figure")
		#print figure_list
		extract_drawing(library_Component, figure_list)	
		
	
	interface = view.get_object("interface")	
	symbol  = interface.get_object("symbol") 
	if (symbol!=None):					
		property_list = search_edif_objects(symbol, "property")	
		if (property_list!=None):				
			for property in property_list:
				p1 = extract_edif_str_param(property, 0)[0]
				if (p1=="VALUE"):
					stringDisplay = property.get_object("string.stringDisplay")
					if (stringDisplay!=None):
						value = stringDisplay.get_param(0)						
						pt = stringDisplay.get_object("display.origin.pt")
						if (pt!=None):							
							value_x, value_y = convert_kicad_coor( extract_edif_pt(pt) )

		figure_list = search_edif_objects(symbol, "figure")
		extract_drawing(library_Component, figure_list)			
	
		port_impl_list = search_edif_objects(symbol, "portImplementation")			
		port_list = search_edif_objects(interface, "port")				
		extract_connections(library_Component, port_impl_list, port_list)			
	
	designator = interface.get_object("designator")
	if (designator!=None):
		#print "designator = "+extract_str_param(designator, 0)[1]
		
		ref = extract_edif_str_param(designator, 0)[1]
		ref = remove_quote(ref)
		if (ref.endswith('?')):
			ref = ref[:-1]
		#print ref
						
		library_Component.set_designator(ref)
						
		pt = interface.get_object("symbol.keywordDisplay.display.origin.pt")
		if (pt!=None):
			x, y = convert_kicad_coor( extract_edif_pt(pt) )					

			library_Component.addField({'id':0, 'ref':add_quote(ref), 'posx':x, 'posy':y})				
			library_Component.addField({'id':1, 'ref':add_quote(cell_name[0]), 'posx':value_x, 'posy':value_y})
			library_Component.addField({'id':2, 'ref':'""', 'posx':0, 'posy':0})
			library_Component.addField({'id':3, 'ref':'""', 'posx':0, 'posy':0})

	return library_Component
	
	
def extract_kicad_library(kicad_library, edif_library):

	print "new library : ", edif_library.get_param(0)
	cells = search_edif_objects(edif_library, "cell")
	
	for edif_cell in cells:
		library_Component = extract_kicad_component_library(edif_cell)
		
		kicad_library.addComponent( library_Component ) 
	
	return kicad_library