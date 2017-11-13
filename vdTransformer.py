#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.12
'''
from multiprocessing import Process
from queue import Empty
import os
from vdDataset import VdDataset
from vdFile import VdFile
from vdConfig import VdConfig
import signal

class VdTransformer(Process):
    '''
    Erzeugt einen Prozess zum Umwandeln von binaeren Daten des 
    Velodyne VLP-16 zu TXT-Dateien
    '''

    def __init__(self, warteschlange, nummer, admin, weiterUmformen, masterSkript):
        '''
        Konstruktor fuer Transformer-Prozess, erbt von multiprocessing.Process
        '''
        # Konstruktor der Elternklasse
        Process.__init__(self)
        
        # Parameter sichern
        self.warteschlange = warteschlange
        self.nummer = nummer
        self.admin = admin
        self.weiterUmformen = weiterUmformen
        self.masterSkript = masterSkript
        
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signal, frame):
        self.masterSkript.ende()
        
    def run(self):
        '''
        Ausfuehrung des Prozesses
        '''
        
        if self.admin:
            os.nice(-15)
        # Erzeugen einer TXT-Datei pro Prozess
        
        oldFolder = ""
        # Dauerschleife
        while self.weiterUmformen.value:
            try:
                # Dateinummer aus Warteschleife abfragen und oeffnen
                filename = self.warteschlange.get(True, 1)
                folder = os.path.dirname(filename)
                if dir != oldFolder :
                    file = VdFile("txt", folder+"/file"+str(self.nummer))
                    oldFolder = folder
                    
                self.oldDir = dir
                
                f = open(filename, "rb")
                
                # Anzahl an Datensaetzen in Datei pruefen
                fileSize = os.path.getsize(f.name)
                cntDatasets = int(fileSize/1206)
                
                for i in range(cntDatasets):
                    # naechsten Datensatz lesen
                    vdData = VdDataset(f.read(1206))
                    
                    # Daten konvertieren und speichern
                    vdData.convertData()
                    
                    # Datensatz zu Datei hinzufuegen
                    file.addDataset(vdData)
                    
                # Datei schreiben
                file.writeTxt()
                # Txt-Datei schliessen
                f.close()
                # Bin-Datei ggf. loeschen
                if VdConfig.binNachTransLoeschen:
                    os.remove(f.name)
            except Empty:
                continue
                
