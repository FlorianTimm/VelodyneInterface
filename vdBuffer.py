#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.10.27
'''

from vdInterface import VdInterface
from multiprocessing import Process
import os
from vdConfig import VdConfig

class VdBuffer(Process):
    '''
    Prozess zum buffern von binaeren Dateien
    '''
    

    def __init__(self, folder, noBreak, scannerStatus, datensaetze, 
                 warteschlange, admin):
        '''
        Constructor
        '''
        # Konstruktor der Elternklasse
        Process.__init__(self)
        
        # Pipes sichern
        self.folder = folder
        self.noBreak = noBreak
        self.scannerStatus = scannerStatus
        self.datensaetze = datensaetze
        self.warteschlange = warteschlange
        self.admin = admin
        
        self.dateiNummer = 0
        
    def run(self):
        # Socket zum Scanner oeffnen
        sock = VdInterface.getDataStream()
        self.scannerStatus.value = "Socket verbunden"
        
        # Variablen initialisieren
        minibuffer = b''
        j = 0
        
        
        # Prozessprioritaet hochschalten, sofern Adminrechte
        if self.admin:
            os.nice(-18)
            
        # Dauerschleife, solange kein Unterbrechen-Befehl kommt
        while self.noBreak.value:
            # Daten vom Scanner holen
            data = sock.recvfrom(1248)[0]
            # RAM-Buffer
            minibuffer += data
            j += 1
            # Alle 5 bzw. 10 Sekunden Daten speichern 
            # oder wenn Abbrechenbefehl kommt
            if (j >= 1500*5 or not self.noBreak.value):
                # Datei schreiben
                f = open(self.folder+"/"+str(self.dateiNummer)+".bin", "wb")
                f.write(minibuffer)
                
                f.close()
                
                self.datensaetze.value += j
                if VdConfig.activateTransformer:
                    self.warteschlange.put(self.dateiNummer)
                
                #Buffer leeren
                minibuffer = b''# 
                j = 0
                
                # Dateizaehler
                self.dateiNummer += 1
            
            if data=='QUIT': 
                break
        f.close()
        sock.close()
        self.scannerStatus.value = "Aufnahme gestoppt"
        print ("Verbindung getrennt")
