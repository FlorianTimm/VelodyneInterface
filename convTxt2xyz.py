#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.20
"""
import configparser

from velodyneInterface.vdFile import VdXYZFile

fileName = "/ssd/daten/ThesisMessung/tief1/file0.txt"

conf = configparser.ConfigParser()
conf.read("velodyneInterface/config.ini")

f = VdXYZFile(conf, "tief")
f.read_from_txt_file(fileName, True)
