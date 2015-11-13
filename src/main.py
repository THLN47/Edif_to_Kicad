#!/usr/bin/env python

import os
import argparse
import sys



from edif_parse_sch import *
from edif_parse_lib import *
	
		


def kicad_append(kicad_list, kicad_object):
	if (kicad_object!=None):
		kicad_list.append(kicad_object)	

		
def parse_libraries(parent_edif_object, output_path=".", project_name="TestTemplate"):	

	libraries = search_edif_objects(parent_edif_object, "library")	
	kicad_library = Kicad_Library(output_path+"/"+project_name+"-cache")

	if libraries!=None:
		for edif_library in libraries:
			extract_kicad_library(kicad_library, edif_library)
	
	kicad_library.save()

	return kicad_library
	
	
def parse_schematic(parent_edif_object, filename, project_name="TestTemplate"):
			
	schematic = Kicad_Schematic(filename, project_name)			
			
		
	edif_instances = search_edif_objects(parent_edif_object, "instance")
	edif_nets = search_edif_objects(parent_edif_object, "net")
	edif_ports = search_edif_objects(parent_edif_object, "portImplementation")
		
	kicad_components = []
		#kicad_noconnections = []
		
	for instance in edif_instances:
		kicad_append(kicad_components, extract_kicad_component(instance))
		#kicad_append(kicad_noconnections, extract_kicad_noconnection(instance))

	
	kicad_wires_list = []
	kicad_net_aliases_list = []
	kicad_junctions_list = []
	for edif_net in edif_nets:
		kicad_append(kicad_wires_list, extract_kicad_wires(edif_net))
	
		kicad_append(kicad_net_aliases_list, extract_kicad_net_aliases(edif_net))
		
		kicad_append(kicad_junctions_list, extract_kicad_junctions(edif_net))
		
	kicad_ports = []
	for edif_port in edif_ports:
		kicad_append(kicad_ports, extract_kicad_port(edif_port) )
		
	

	
	schematic.add_kicad_object( kicad_components )
	#schematic.add_kicad_object( kicad_noconnections )		
	schematic.add_kicad_object( kicad_ports )		
	schematic.add_kicad_object( kicad_wires_list )
	schematic.add_kicad_object( kicad_net_aliases_list )
	schematic.add_kicad_object( kicad_junctions_list )	
	
	schematic.save()
		
	return schematic


	
	



if __name__ == "__main__": 

	parser = argparse.ArgumentParser()
	parser.add_argument('input')	
	args = parser.parse_args()
	
	filename  = args.input
	
	path = os.path.dirname(filename)
	project_name = os.path.basename(filename).split('.')[0]
	
	output_path = path+"/kicad_"+project_name+"/"
	
	print "output path =", output_path
	print "project name = ", project_name
	
	if (not os.path.exists(output_path)):
		os.makedirs(output_path)
		

	
	edif_root = Read_Edif_file(filename)
	
	
	edif_object = edif_root.get_object("edif") 
	if (edif_object!=None):
		obj = edif_object.get_object("edifversion")
		version = obj.get_params( [0, 1, 2] )
		if (version!=None):
			if ( (version[0]=='2') and (version[1]=='0') and(version[2]=='0') ):
				print "Edif 2.0.0 checked ;)"
			
				parse_libraries(edif_object, output_path, project_name)
					
				print "---------------------------------------------"	
				pages = search_edif_objects(edif_object, "page")
				
				page_nb = 0
				for page in pages:
					page_nb+=1
					filename = output_path+"page"+str(page_nb)
					print filename
					parse_schematic(page, filename, project_name)
					

					
	sys.exit(0)
