#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.12.11
"""

import configparser
import os
from glob import glob
from vdDataset import VdDataset
from vdTxtFile import VdTxtFile
from vdXYZFile import VdXYZFile
from vdSQLite import VdSQLite
from vdObjFile import VdObjFile

# load config file
conf = configparser.ConfigParser()
conf.read("config.ini")

pfad = input("Pfad zu bin-Dateien:")
new_filename = input("Neuer Dateiname:")
format = input("Dateiformat (xyz,txt,obj,sql):")

fs = glob(pfad + "/*.bin")

if len(fs) > 0:

    for filename in fs:
        folder = os.path.dirname(filename)
        new_file = None
        if format == "sql":
            new_file = VdSQLite(conf, folder + "/" + new_filename)
        elif format == "txt":
            new_file = VdTxtFile(conf, folder + "/" + new_filename)
        elif format == "obj":
            new_file = VdObjFile(conf, folder + "/" + new_filename)
        elif format == "xyz":
            new_file = VdXYZFile(conf, folder + "/" + new_filename)

        print(filename)

        bin_file = open(filename, "rb")

        # Calculate number of datasets
        fileSize = os.path.getsize(bin_file.name)
        print("FileSize: " + str(fileSize))
        cntDatasets = fileSize // 1206
        print("Datasets: " + str(cntDatasets))

        for i in range(cntDatasets):
            vdData = VdDataset(conf, bin_file.read(1206))
            vdData.convert_data()
            new_file.write_data(vdData.get_data())
        bin_file.close()
    new_file.close()
