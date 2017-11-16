#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.15
'''

from vdInterface import VdInterface
import socket
from multiprocessing import Process
import os
from datetime import datetime
import signal


class VdBuffer(Process):

    """
    Prozess zum Buffern von binaeren Dateien
    """

    def __init__(self, masterSkript):
        '''
        Constructor
        '''
        # Konstruktor der Elternklasse
        Process.__init__(self)

        # Pipes sichern
        self._masterSkript = masterSkript
        self._noBreak = masterSkript.noBreak
        self._scannerStatus = masterSkript.scannerStatus
        self._datensaetze = masterSkript.datensaetze
        self._warteschlange = masterSkript.warteschlange
        self._admin = masterSkript.admin
        self._date = masterSkript.date
        self._conf = masterSkript.conf

        self._dateiNummer = 0

    def _signal_handler(self, signal, frame):
        # self.masterSkript.ende()
        print("SIGINT vdBuffer")

    def _neuerOrdner(self):
        # Uhrzeit abfragen fuer Laufzeitlaenge und Dateinamen
        self._date.value = datetime.now()
        self._folder = self._conf.get("Datei", "fileNamePre")
        self._folder += self._date.value.strftime(
            self._conf.get("Datei", "fileTimeFormat"))
        # Speicherordner anlegen und ausgeben
        os.makedirs(self._folder)
        print ("Speicherordner: " + self._folder)

    def run(self):
        
        signal.signal(signal.SIGINT, self._signal_handler)

        # Socket zum Scanner oeffnen
        sock = VdInterface.getDataStream(self._conf)
        self._scannerStatus.value = "Socket verbunden"

        # Variablen initialisieren
        minibuffer = b''
        j = 0
        
        self._datensaetze.value = 0

        # Prozessprioritaet hochschalten, sofern Adminrechte
        if self._admin:
            os.nice(-18)
            
        transformer = self._conf.get("Funktionen", "activateTransformer")
        messungProDatensatz = int(self._conf.get(
                    "Geraet", "messungProDatensatz"))

        # Dauerschleife, solange kein Unterbrechen-Befehl kommt

        sock.settimeout(1)
        while self._noBreak.value:
            try:
                # Daten vom Scanner holen
                data = sock.recvfrom(1248)[0]

                if (j == 0 and self._dateiNummer == 0):
                    self._neuerOrdner()
                # RAM-Buffer
                minibuffer += data
                j += 1
                self._datensaetze.value += messungProDatensatz
                # Alle 5 bzw. 10 Sekunden Daten speichern
                # oder wenn Abbrechenbefehl kommt
                if (j >= 1500) or (not self._noBreak.value):
                    # Datei schreiben
                    f = open(
                        self._folder + "/" + str(self._dateiNummer) + ".bin",
                        "wb")
                    f.write(minibuffer)

                    f.close()

                    if transformer:
                        self._warteschlange.put(f.name)

                    # Buffer leeren
                    minibuffer = b''   
                    j = 0

                    # Dateizaehler
                    self._dateiNummer += 1

                if data == 'QUIT':
                    break
            except socket.timeout:
                print ("Keine Daten")
                continue
        sock.close()
        self._scannerStatus.value = "Aufnahme gestoppt"
        print ("Verbindung getrennt")
