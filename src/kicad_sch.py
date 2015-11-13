#!/usr/bin/env python

import math
import time

from kicad_common import *

def convert_kicad_coor(pt):
	K = 10
	return [pt[0]*K, -pt[1]*K]	

class RotMat(object):
	_mat = []

	def __init__(self):			
		names = []
		values = []
		for i in range(0, 4):
			rotdeg = str(90*(i))
					
			a = (i+1)*math.pi / 2
			cos_a = int(math.cos(a))
			sin_a = int(math.sin(a))
					
			names.append('R'+rotdeg)
			values.append( [sin_a, cos_a, cos_a, -sin_a] )

			if (rotdeg=='0'):
				names.append( 'MY')		
				values.append( [-sin_a, -cos_a, cos_a, -sin_a] )				
			else:
				names.append( 'MYR'+rotdeg)					
				values.append( [sin_a, cos_a, -cos_a, sin_a] )
								
			if (rotdeg=='0'):
				names.append( 'MX')
				values.append( [sin_a, cos_a, -cos_a, sin_a] )
			else:
				names.append( 'MXR'+rotdeg)					
				values.append( [-sin_a, -cos_a, cos_a, -sin_a] )

			
		self._mat = dict(zip(names, values))		
		#print self._mat
		
	def get_matrice(self, orientation):
		try:
			ret = self._mat[orientation]
		except KeyError:
			print "*** ERROR unkwnon orientation '",orientation,"'"
			ret = None
		return ret
		
	def str_matrice(self, orientation):
		try:
			ret = " ".join(str(coef) for coef in self._mat[orientation])
		except KeyError:
			print "*** ERROR unkwnon orientation '",orientation,"'"
			ret = None
		return ret
	
	def debug(self):
		for k in self._mat:
			print k, ":", self._mat[k]
	
	
rotMat = RotMat()			


		
		
class Kicad_Wire(object):	

	def __init__(self, x1, y1, x2, y2):
		self._wire = [x1, y1, x2, y2]
		
	def output(self):
		to_write = "Wire Wire Line\n\t"
		to_write += " ".join(str(coor) for coor in self._wire)
		to_write += "\n"
		return [to_write]
		

# Text Label 7450 2650 0    60   ~ 0
# "test_label"		
class Kicad_NetAlias(object):
	def __init__(self, x, y, text):
		self._pt = [x, y]
		self.text = text

	def output(self):
		to_write = "Text Label "
		to_write += " ".join(str(coor) for coor in self._pt) 
		to_write += " 0"
		to_write += " 60" # size
		to_write += " ~"
		to_write += " 0\n"
		text = remove_quote(self.text) 
		text = text.replace("\\\"", "\"")
		to_write += text
		to_write += "\n"
		return [to_write]

# NoConn ~ 2900 1300
class Kicad_NoConnection(object):

	def __init__(self, x, y):
		self._pt = [x, y]
		
	def output(self):
		to_write = "NoConn ~ " 
		to_write += " ".join(str(coor) for coor in self._pt) 
		to_write += "\n"
		return [to_write]		
		
class Kicad_Junction(object):

	def __init__(self, x, y):
		self._pt = [x, y]
		
	def output(self):
		to_write = "Connection ~ " 
		to_write += " ".join(str(coor) for coor in self._pt) 
		to_write += "\n"
		return [to_write]
		
		
		
class Kicad_TextPort(object):

	def __init__(self, name, x, y):	
		self.name = name
		self._pt = [x, y]
		self.port_type = "UnSpc"
		self.rotation = "2"		
		
	def set_text(self, text):	
		self.text = decode_special_char(text)
		

	def set_type(self, port_type):
		self.port_type = port_type
	
		
	def set_rotation(self, rotation):
		self.rotation = rotation
		"""
		key_rot_def = {'R':0, 'U':1, 'L':2, 'D':3}
		try:
			self.rotation = key_rot_def[rot]
		except KeyError :
			pass
		"""
	def output(self):
		to_write = "Text GLabel "
		to_write += " ".join(str(coor) for coor in self._pt) 
		to_write += " "+str( self.rotation )
		to_write += " 50"
		to_write += " "+self.port_type
		to_write += " ~"
		to_write += " 0\n"
		text = remove_quote(self.text) 
		text = text.replace("\\\"", "\"")
		to_write += text
		to_write += "\n"
		return [to_write]
				
# Text GLabel 2200 1600 0    60   Input ~ 0
# "test"


class Kicad_Schematic_Component(object):

	_L_KEYS = ['name', 'ref']
	_U_KEYS = ['unit', 'convert', 'time_stamp']
	_P_KEYS = ['posx', 'posy']
	_AR_KEYS = ['path', 'ref', 'part']
	_F_KEYS = ['id', 'ref', 'orient', 'posx', 'posy', 'size', 'attributs', 'hjust', 'props', 'name']

	_KEYS = {'L':_L_KEYS, 'U':_U_KEYS, 'P':_P_KEYS, 'AR':_AR_KEYS, 'F':_F_KEYS}

	def __init__(self, name, ref):
		self.name = name
		
		self.labels = {}
		self.unit = {}
		self.position = {}
		self.references = []
		self.fields = []
		
	
		ref = decode_special_char(ref)
		
		values = [name, ref]
		self.labels = dict(zip(self._L_KEYS, values))

		ts = str(hex(int(time.time()))[2:]).upper()
		values = ['1', '1', ts]
		self.unit = dict(zip(self._U_KEYS, values))
		
		self.unit_part = '1'
		self.orientation = "R0"
				
	def set_orientation(self, orientation):
		#print self.name, "set_orientation:", orientation
		self.orientation = orientation	
		
	def set_position(self, x, y):
		self.position = {'posx':x, 'posy':y}
		#self.position = [x, y]
			
	def addField(self, field_data):
		def_field = {'id':None, 'ref':None, 
			'orient':'H', 
			'posx':'0', 
			'posy':'0', 
			'size':'50', 
			'attributs':'0000', 
			'hjust':'C', 
			'props':'CNN', 
			'name':''}

		#field_data['posx'], field_data['posy'] = convert_kicad_coor(field_data['posx'], field_data['posy'])
		
		for key, value in field_data.items():
			field_data[key] = decode_special_char(str(value))
			
		# merge dictionaries and set the id value
		field = dict(list(def_field.items()) + list(field_data.items()))
		field['id'] = str(len(self.fields))

		self.fields.append(field)
		return field
		

		
	def output(self):
		global rotMat
		
	
		to_write = '$Comp\n'
		
		component = self
		
		if component.labels:
			line = 'L '
			for key in component._L_KEYS:
				line += component.labels[key] + ' '
			to_write += line.rstrip() + '\n'

		if component.unit:
			line = 'U '
			for key in component._U_KEYS:
				line += component.unit[key] + ' '
			to_write += line.rstrip() + '\n'

		if component.position:
			line = 'P '
			for key in component._P_KEYS:
				line += str( component.position[key] ) + ' '
			to_write += line.rstrip() + '\n'

		for reference in component.references:
			if component.references:
				line = 'AR '
				for key in component._AR_KEYS:
					line += reference[key] + ' '
				to_write += line.rstrip() + '\n'

		for field in component.fields:
			line = 'F '
			for key in component._F_KEYS:
				line += field[key] + ' '
			to_write += line.rstrip() + '\n'
				
		# to_write += ['\t'+  self.unit_part + " " + self.position['posx'] + " " + self.position['posy']] + ['\n']	
		
		str_pos = ' '
		for key in component._P_KEYS:
			str_pos += str( component.position[key] ) + ' '
				
		to_write += '\t' +  self.unit_part + str_pos + '\n'
		#print self.orientation
		to_write += '\t' + str( rotMat.str_matrice(self.orientation) ) + '\n'
		to_write += '$EndComp\n'
		
		return [to_write]
		
		
		
"""		
class Kicad_Sheet(object):
	_S_KEYS = ['topLeftPosx', 'topLeftPosy','botRightPosx', 'botRightPosy']
	_U_KEYS = ['uniqID']
	_F_KEYS = ['id', 'value', 'IOState', 'side', 'posx', 'posy', 'size']

	_KEYS = {'S':_S_KEYS, 'U':_U_KEYS, 'F':_F_KEYS}
	
	def __init__(self, data):	
		self.shape = {}
		self.unit = {}
		self.fields = []
"""	
	
	

class Kicad_Schematic(object):
	
	def __init__(self, filename, project_name):
		self.filename = filename	
		self.project_name = project_name
		self.kicad_object_list = []
		
	def add_kicad_object(self, kicad_object):
		if (kicad_object!=None):
			self.kicad_object_list.append(kicad_object)
		
		
	def __output(self, kicad_element):
		to_write = []
		if (isinstance(kicad_element, list)):
			for ele in kicad_element:
				to_write += self.__output(ele)
		else:
			to_write += kicad_element.output()
			#for line in to_write:
			#	print line,
		return to_write

	
		
	def output(self):
	
		#pprint.pprint(self.kicad_object_list)

		to_write = self.__output(self.kicad_object_list)		

		return to_write		
		
		
	def save(self, filename=None):
	
		if not filename:
			filename = self.filename+".sch"

		to_write = []
		
		template_header_sch = ['EESchema Schematic File Version 2',
							'LIBS:'+self.project_name+'-cache',
							'EELAYER 25 0',
							'EELAYER END',
							'$Descr A3 16535 11693',
							'encoding utf-8',
							'Sheet 1 1',
							'Title ""',
							'Date "',
							'Rev ""',
							'Comp ""',
							'Comment1 ""',
							'Comment2 ""',
							'Comment3 ""',
							'Comment4 ""',
							'$EndDescr']
			
		for s in template_header_sch:
			to_write += [ s+"\n" ]	
		
		to_write += self.output()
		
		to_write += ['$EndSCHEMATC']
		to_write += ['\n']
		
		f = open(filename, 'w')
		f.writelines(to_write)
		f.close()		
		