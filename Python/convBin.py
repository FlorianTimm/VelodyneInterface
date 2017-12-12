#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.12.12
"""

import configparser
import os
from glob import glob
import subprocess
from vdDataset import VdDataset
from vdTxtFile import VdTxtFile
from vdXYZFile import VdXYZFile
from vdSQLite import VdSQLite
from vdObjFile import VdObjFile

# load config file
conf = configparser.ConfigParser()
conf.read("config.ini")

pfad = input("Pfad zu bin-Dateien (/test/ordner):")
new_filename = input("Neuer Dateiname:")
fformat = input("Dateiformat (xyz,txt,obj,sql):")

trans = conf.get("file", "transformer")

fs = glob(pfad + "/*.bin")

if len(fs) > 0:

    for filename in fs:
        folder = os.path.dirname(filename)
        new_file = folder + "/" + new_filename

        # python transformer
        if trans == "python":
            new_file = None
            if fformat == "sql":
                new_file = VdSQLite(conf, new_file)
            elif fformat == "txt":
                new_file = VdTxtFile(conf, new_file)
            elif fformat == "obj":
                new_file = VdObjFile(conf, new_file)
            elif fformat == "xyz":
                new_file = VdXYZFile(conf, new_file)

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

        # c++ transformer
        else:
            result = subprocess.run(
                ['./' + trans,
                 "bin",
                 filename,
                 fformat,
                 new_file],
                stdout=subprocess.PIPE)
            print(result.stdout.decode('utf-8'))

    if trans == "python":
        new_file.close()
