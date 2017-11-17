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
vd_file = None

for filename in fs:
    print(filename)
    # Dateinummer aus Warteschleife abfragen und oeffnen
    folder = os.path.dirname(filename)
    if vd_file is None:
        vd_file = VdObjFile(
            conf,
            folder + "/vd_file")

    f = open(filename, "rb")

    # Anzahl an Datensaetzen in Datei pruefen
    fileSize = os.path.getsize(f.name)
    cntDatasets = int(fileSize / 1206)

    for i in range(cntDatasets):
        # naechsten Datensatz lesen
        vdData = VdDataset(conf, f.read(1206))

        # Daten konvertieren und speichern
        vdData.convert_data()

        # Datensatz zu Datei hinzufuegen
        vd_file.write_data(vdData.get_data())

    # Datei schreiben
    # Txt-Datei schliessen
    f.close()
