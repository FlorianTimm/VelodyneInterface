#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.19
"""
from vdFile import VdObjFile
import configparser

fileName = "BeispielDateien/test.txt"

conf = configparser.ConfigParser()
conf.read("config.ini")

f = VdObjFile(conf, fileName)
f.read_from_txt_file(fileName, True)
