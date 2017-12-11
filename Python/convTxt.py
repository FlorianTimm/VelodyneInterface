#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.12.11
"""
import configparser
import os

from vdTxtFile import VdTxtFile
from vdXYZFile import VdXYZFile
from vdSQLite import VdSQLite
from vdObjFile import VdObjFile

filename = input("TXT-Datei:")
new_filename = input("Neuer Dateiname:")
fileformat = input("Dateiformat (xyz,txt,obj,sql):")

conf = configparser.ConfigParser()
conf.read("config.ini")

folder = os.path.dirname(filename)

new_file = None
if fileformat == "sql":
    new_file = VdSQLite(conf, folder + "/" + new_filename)
elif fileformat == "txt":
    new_file = VdTxtFile(conf, folder + "/" + new_filename)
elif fileformat == "obj":
    new_file = VdObjFile(conf, folder + "/" + new_filename)
elif fileformat == "xyz":
    new_file = VdXYZFile(conf, folder + "/" + new_filename)
new_file.read_from_txt_file(filename, True)
