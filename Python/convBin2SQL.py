#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.20
"""

import configparser
import os
from glob import glob

from velodyneInterface.vdDataset import VdDataset

from vdFile import VdSQLite

# load config file
conf = configparser.ConfigParser()
conf.read("config.ini")

fs = glob(
    "/ssd/daten/ThesisMessung/tief1_bin/*.bin")

if len(fs) > 0:
    folder = os.path.dirname(fs[0])
    sql_lite = VdSQLite(
        conf,
        folder + "/file")

    for filename in fs:
        print(filename)

        bin_file = open(filename, "rb")

        # Calculate number of datasets
        fileSize = os.path.getsize(bin_file.name)
        cntDatasets = int(fileSize / 1206)

        for i in range(cntDatasets):
            vdData = VdDataset(conf, bin_file.read(1206))
            vdData.convert_data()
            sql_lite.write_data(vdData.get_data())
        bin_file.close()
    sql_lite.close()
