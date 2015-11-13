#!/usr/bin/env python

import imp
"""
	path to Edif_parser_mod
"""
path_to_Edif_parser_mod = '../../Edif_parser/Edif_parser_mod'

Edif_parser_mod = imp.load_source('Edif_parser_mod', path_to_Edif_parser_mod+'/Edif_parser.py')