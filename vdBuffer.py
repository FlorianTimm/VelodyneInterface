#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.12
'''

from vdInterface import VdInterface
import socket
from multiprocessing import Process
import os
from vdConfig import VdConfig
from datetime import datetime

class VdBuffer(Process):
    '''
    Prozess zum buffern von binaeren Dateien
    '''
    

    def __init__(self, noBreak, scannerStatus, datensaetze, 
                 warteschlange, admin, date):
        '''
        Constructor
        '''
        # Konstruktor der Elternklasse
        Process.__init__(self)
        
        # Pipes sichern
        self.noBreak = noBreak
        self.scannerStatus = scannerStatus
        self.datensaetze = datensaetze
        self.warteschlange = warteschlange
        self.admin = admin
        self.date = date  
        
        self.dateinummer = 0
        
        
    def neuerOrdner (self):
        # Uhrzeit abfragen fuer Laufzeitlaenge und Dateinamen
        self.date.value = datetime.now()
        self.folder = self.date.value.strftime(VdConfig.fileTimeFormat) 
        # Speicherordner anlegen und ausgeben
        os.makedirs(self.folder)  
        print ("Speicherordner: " + self.folder) 
         
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
        
        sock.settimeout(1)
        while self.noBreak.value:
            try:
                # Daten vom Scanner holen
                data = sock.recvfrom(1248)[0]
                
                if (j == 0 and self.dateinummer == 0):
                    neuerOrdner()
                # RAM-Buffer
                minibuffer += data
                j += 1
                self.datensaetze.value += 1
                # Alle 5 bzw. 10 Sekunden Daten speichern 
                # oder wenn Abbrechenbefehl kommt
                if (j >= 1500*5 or not self.noBreak.value):
                    # Datei schreiben
                    f = open(self.folder+"/"+str(self.dateiNummer)+".bin", "wb")
                    f.write(minibuffer)
                    
                    f.close()
                    
                    if VdConfig.activateTransformer:
                        self.warteschlange.put(f.name)
                    
                    #Buffer leeren
                    minibuffer = b''# 
                    j = 0
                    
                    # Dateizaehler
                    self.dateiNummer += 1
                
                if data=='QUIT': 
                    break
            except socket.timeout:
                continue
        sock.close()
        self.scannerStatus.value = "Aufnahme gestoppt"
        print ("Verbindung getrennt")
