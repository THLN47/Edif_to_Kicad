#!/usr/bin/env python
	
from kicad_sch import *

from Edif_parser_mod import *	

def extract_kicad_noconnection(instance):
	noconnections = []
	portInstances = search_edif_objects(instance, "portInstance")
	for portInstance in portInstances:		
		properties = search_edif_objects(portInstance, "property")
		for property in properties:
			if (property.get_param(0)=="TERMINATOR"):
				string = property.get_object("string")				
				if (string!=None):
					if (string.get_param(0)=='"TRUE"'):					
						# solution ci-dessous ne place pas correctement le symbole X
						pt = portInstance.get_object("designator.stringDisplay.display.origin.pt")
						if (pt!=None):							
							x, y = convert_kicad_coor( extract_edif_pt(pt) )
							noconnections.append( Kicad_NoConnection(x, y) )
							
						# @TODO : il faut calculer le point a partir du composant dans la librairie :
						# trop galere pour l'instant ...
							
	#pprint.pprint(noconnections)							
	if (len(noconnections)==0):
		return None
	else:
		return noconnections					


	
def extract_kicad_component(instance):
	viewRef = instance.get_object("viewRef")
	cellRef = viewRef.get_object("cellRef")	
	libname = ""+viewRef.get_param(0)
	#libname = "IMPORT_"+cellRef.get_param(0)


	stringDisplay = instance.get_object("designator.stringDisplay")
	if (stringDisplay!=None):
		refDesign = stringDisplay.get_param(0)
		# Position designator
		pt = stringDisplay.get_object("display.origin.pt")
		if (pt!=None):
			x, y = convert_kicad_coor( extract_edif_pt(pt) )
		f0_data = {'ref':refDesign, 'posx':x, 'posy':y}
	else:
		return None
		
		
	kicad_component = Kicad_Schematic_Component(libname, refDesign)
	
	# posistion
	pt = instance.get_object("transform.origin.pt")
	if (pt!=None):
		component_x, component_y = convert_kicad_coor( extract_edif_pt(pt) )
		kicad_component.set_position(component_x, component_y)
	
	# orientation
	orientation = instance.get_object("transform.orientation")
	if (orientation!=None):
		orientation = orientation.get_param(0)
		kicad_component.set_orientation(orientation)
		
	# value
	properties = search_edif_objects(instance, "property")
	for property in properties:
		rename = property.get_object_param("rename", "VALUE")			
		if (rename!=None):
			stringDisplay = property.get_object("string.stringDisplay")
			value = stringDisplay.get_param(0) 
			
			pt = stringDisplay.get_object("display.origin.pt")
			if (pt!=None):
				x, y = convert_kicad_coor( extract_edif_pt(pt) )
			f1_data = {'ref': value, 'posx':x, 'posy':y}
	
		
	
	f2_data = {'ref': '""',  'posx':component_x, 'posy':component_y, 'attributs':'0001'}
	f3_data = {'ref': '""',  'posx':component_x, 'posy':component_y, 'attributs':'0001'}	
			
		
	kicad_component.addField(f0_data)
	kicad_component.addField(f1_data)	
	kicad_component.addField(f2_data)
	kicad_component.addField(f3_data)	
	return kicad_component
	 
			

	
def extract_kicad_wires(edif_net):

	wires = []
	figures = search_edif_objects(edif_net, "figure")	
	for figure in figures:
		if (figure!=None):
			if (figure.get_param(0) == "WIRE"):
				pts = figure.get_object("path.pointList")						
				for i in range(0, pts.get_nb_param()):					
					pt = pts.get_param(i)					
					x, y = convert_kicad_coor( extract_edif_pt(pt) )
					if (i>0):
						wire = Kicad_Wire(xn, yn, x, y)
						wires.append( wire )
					xn, yn = [x, y]
			
	if (len(wires)==0):
		return None
	else:
		return wires
		

def extract_kicad_net_aliases(edif_net):
	net_aliases = []
	net_name = extract_edif_str_param(edif_net, 0)
	if (net_name!=None):
		if (type(net_name[0])!=unicode):		
			display_list = search_edif_objects(net_name[0], "display" )
			for display in display_list:
				pt = display.get_object("origin.pt")
				if (pt!=None):
					x, y = convert_kicad_coor( extract_edif_pt(pt) )
					#print net_name[1], x, y
					netAlias = Kicad_NetAlias(x, y, net_name[1])	
					net_aliases.append( netAlias )
				
	if (len(net_aliases)==0):
		return None
	else:
		return net_aliases				
	
		
def extract_kicad_junctions(edif_net):
	junctions = []
	instances = search_edif_objects(edif_net, "instance")	
	for instance in instances:
		if (instance!=None):
			id = instance.get_param(0)
			pt = instance.get_object("transform.origin.pt")
			if (pt!=None):
				x, y = convert_kicad_coor( extract_edif_pt(pt) )
				junction = Kicad_Junction( x, y )
				junctions.append(junction)
				
	if (len(junctions)==0):
		return None
	else:
		return junctions	
	
	

def extract_kicad_port(edif_port):
	# p1
	p1 = edif_port.get_param(0)
	if (type(p1)==unicode):
		p1_type = None	
		p1_name = p1
	else:
		p1_type = p1.get_context()
		if (p1_type=="name"):
			# text module 
			p1_name = p1.get_param(0)
			display = p1.get_object("display")
			if (display!=None):
				p1_type = display.get_param(0)
				pt = display.get_object("origin.pt")
				if (pt!=None):
					p1_x, p1_y = convert_kicad_coor( extract_edif_pt(pt) )

					#print p1_x, p1_y
		#print p1_type, p1_name


	# p2
	instance = edif_port.get_object("instance")
	p2_name = extract_edif_str_param(instance, 0)	
	#print p2_name
			
	viewRef = instance.get_object("viewRef")
	name = viewRef.get_param(0)
		
	"""
	pt = instance.get_object("transform.origin.pt")
	if (pt!=None):
		component_x, component_y = extract_pt(pt)
	"""
	orientation = instance.get_object("transform.orientation") 
	if (orientation!=None):
		orientation = orientation.get_param(0)
	else:
		orientation = "R0"
	
	pt = edif_port.get_object("connectLocation.figure.dot.pt")
	if (pt!=None):
		component_x, component_y = convert_kicad_coor( extract_edif_pt(pt) )	
	else:
		return

	if (p1_type=="MODULETEXT"):
			
		textPort = Kicad_TextPort(p1_name, component_x, component_y)

		name, rot = name.split("_")
		name = name.replace("PORT", "")
		
		if (name=="BOTH"):
			port_type = "BiDi"
		elif (name=="LEFT"):
			port_type = "Output"
		elif (name=="RIGHT"):
			port_type = "Input"
		else:
			port_type = "UnSpc"
		
		if (rot=="L"):
			a = 1
		else:
			a = 0
		

		def_rot = {
			"R0":[0, 2],
			"R90":[3, 1],
			"R180":[2, 0],
			"R270":[1, 3],
			
			"MY":[2, 0],
			"MYR90":[1, 3],
			#"MYR180":[0, 2],
			#"MYR270":[1, 3],

			"MX":[0, 2],
			"MXR90":[3, 1],
			#"MXR180":[0, 2],
			#"MXR270":[1, 3]			
			}
		comb_angle = def_rot[orientation][a]
			
		#print name, rot, orientation, comb_angle
	
		
		textPort.set_text(p2_name[1])
		textPort.set_type(port_type)
		textPort.set_rotation(comb_angle)
		
		return textPort
		
	

	ref = "\""+name+"\""	
	value = "\""+p1_name+"\""
	
	x = component_x
	y = component_y
	
	f0_data = {'ref': ref, 'posx':x, 'posy':y}
	f1_data = {'ref': value, 'posx':x, 'posy':y}
	f2_data = {'ref': '""',  'posx':component_x, 'posy':component_y, 'attributs':'0001'}
	f3_data = {'ref': '""',  'posx':component_x, 'posy':component_y, 'attributs':'0001'}	
	
	kicad_component = Kicad_Schematic_Component(name, ref)
	kicad_component.set_position(component_x, component_y)
	kicad_component.set_orientation(orientation)
	kicad_component.addField(f0_data)
	kicad_component.addField(f1_data)		
	kicad_component.addField(f2_data)
	kicad_component.addField(f3_data)	
	return kicad_component
