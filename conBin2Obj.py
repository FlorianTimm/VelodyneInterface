#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.15
'''
from multiprocessing import Process
from queue import Empty
import os
from vdDataset import VdDataset
from vdFile import VdFile
from glob import glob
import configparser

# Konfigurationsdatei laden
conf = configparser.ConfigParser()
conf.read("config.ini")

fs = glob("/ssd/daten/ThesisMessung/data2017-11-16T14:06:31_SicherungBin/*.bin")
file = None

for filename in fs:
    print(filename)
    # Dateinummer aus Warteschleife abfragen und oeffnen
    folder = os.path.dirname(filename)
    if file == None:
        file = VdFile(
            conf,
            "obj",
            folder + "/file")
    
    f = open(filename, "rb")
    
    # Anzahl an Datensaetzen in Datei pruefen
    fileSize = os.path.getsize(f.name)
    cntDatasets = int(fileSize / 1206)
    
    for i in range(cntDatasets):
        # naechsten Datensatz lesen
        vdData = VdDataset(conf, f.read(1206))
    
        # Daten konvertieren und speichern
        vdData.convertData()
    
        # Datensatz zu Datei hinzufuegen
        file.writeDataToObj(vdData.getData())
    
    # Datei schreiben
    # Txt-Datei schliessen
    f.close()
