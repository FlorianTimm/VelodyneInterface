#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.15
"""

import os
from vdDataset import VdDataset
from vdFile import VdObjFile
from glob import glob
import configparser

# Konfigurationsdatei laden
conf = configparser.ConfigParser()
conf.read("config.ini")

fs = glob(
    "/ssd/daten/ThesisMessung/data2017-11-16T14:06:31_SicherungBin/*.bin")

if len(fs) > 0:
    folder = os.path.dirname(fs[0])
    vd_file = VdObjFile(
            conf,
            folder + "/file")

    for filename in fs:
        print(filename)

        f = open(filename, "rb")

        # Calculate number of datasets
        fileSize = os.path.getsize(f.name)
        cntDatasets = int(fileSize / 1206)

        for i in range(cntDatasets):
            vdData = VdDataset(conf, f.read(1206))
            vdData.convert_data()
            vd_file.write_data(vdData.get_data())
        f.close()
    vd_file.close()