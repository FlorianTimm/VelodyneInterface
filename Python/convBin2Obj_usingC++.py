#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.20
"""

import configparser
import os
from glob import glob
from time import *

from vdDataset import VdDataset

from vdObjFile import VdObjFile

# load config file
conf = configparser.ConfigParser()
conf.read("config.ini")

fs = glob(
    "/ssd/daten/ThesisMessung/tief*/*.bin")

# fs = ["/ssd/daten/ThesisMessung2/data2017-11-27T13:51:16/4.bin"]

t1 = clock()
if len(fs) > 0:

    for filename in fs:
        folder = os.path.dirname(filename)
        folder_split = folder.split("/")
        new_file = folder_split[-1].replace(":","")
        
        new_file = "/media/timm/TIMM_32GB/tief/" + new_file + ""

        new_file = "/media/timm/TIMM_32GB/tief/tief_gesamt"
        
        print(new_file)
        
        print(filename)
        import subprocess
        result = subprocess.run(['./vdTrans_linux64', "bin", filename, "sql", new_file], stdout=subprocess.PIPE)
        print(result.stdout.decode('utf-8'))
    
t2 = clock()

t = t2 - t1
print ("Laufzeit: " + str(t))
