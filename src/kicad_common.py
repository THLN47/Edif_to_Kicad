#!/usr/bin/env python

import pprint
import re

def remove_quote(string):
	if (string==None):
		return None
		
	if (string.startswith('"') and string.endswith('"')):
		string = string[1:-1]
	return string

def add_quote(string):
	string = string.replace("\"", "\\\"")
	string = "\""+string+"\""
	return string
	
def decode_special_char(string):
	with_quote = False
	
	if string.startswith('"') and string.endswith('"'):
		string = string[1:-1]
		with_quote = True
	
	result = re.findall(r'%(\d+)%', string)		
	if (result!=None):
		for n in result:
			string = string.replace("%"+n+"%", chr(int(n)))
			
	string = string.replace("\"", "\\\"")
	
	if (with_quote):
		string = "\""+string+"\""
		
	return string
	
	
	
