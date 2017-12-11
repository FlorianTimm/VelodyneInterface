#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.12.11
"""

import configparser
import os
from glob import glob

pfad = input("Pfad zu bin-Dateien:")
new_filename = input("Neuer Dateiname:")
format = input("Dateiformat (xyz,txt,obj,sql):")

fs = glob(pfad + "/*.bin")

if len(fs) > 0:

    for filename in fs:
        folder = os.path.dirname(filename)
        new_file = folder + "/" + new_filename

        print(new_file)

        print(filename)
        import subprocess

        result = subprocess.run(
            ['./vdTrans_linux64',
             "bin",
             filename,
             "txt",
             new_file],
            stdout=subprocess.PIPE)
        print(result.stdout.decode('utf-8'))
