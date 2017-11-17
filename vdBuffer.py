#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.17
"""

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

    def __init__(self, master):
        """
        Constructor
        """
        # Konstruktor der Elternklasse
        Process.__init__(self)

        # Pipes sichern
        # self._master = master
        self._go_on_buffering = master.get_go_on_buffer()
        self._scanner_status = master.get_scanner_status()
        self._datasets = master.get_datasets()
        self._queue = master.get_queue()
        self._admin = master.get_root()
        self._date = master.get_date()
        self._conf = master.get_conf()

        self._file_no = 0

    @staticmethod
    def _signal_handler(signal, frame):
        # self.master.ende()
        print("SIGINT vdBuffer")

    def _new_folder(self):
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
        sock = VdInterface.get_data_stream(self._conf)
        self._scanner_status.value = "Socket verbunden"

        # Variablen initialisieren
        minibuffer = b''
        j = 0

        self._datasets.value = 0

        # Prozessprioritaet hochschalten, sofern Adminrechte
        if self._admin:
            os.nice(-18)

        transformer = self._conf.get("Funktionen", "activateTransformer")
        measurements_per_dataset = int(self._conf.get(
            "Geraet", "messungProDatensatz"))

        # Dauerschleife, solange kein Unterbrechen-Befehl kommt

        sock.settimeout(1)
        while self._go_on_buffering.value:
            try:
                # Daten vom Scanner holen
                data = sock.recvfrom(1248)[0]

                if j == 0 and self._file_no == 0:
                    self._new_folder()
                # RAM-Buffer
                minibuffer += data
                j += 1
                self._datasets.value += measurements_per_dataset
                # Alle 5 bzw. 10 Sekunden Daten speichern
                # oder wenn Abbrechenbefehl kommt
                if (j >= 1500) or (not self._go_on_buffering.value):
                    # Datei schreiben
                    f = open(
                        self._folder + "/" + str(self._file_no) + ".bin",
                        "wb")
                    f.write(minibuffer)

                    f.close()

                    if transformer:
                        self._queue.put(f.name)

                    # Buffer leeren
                    minibuffer = b''
                    j = 0

                    # Dateizaehler
                    self._file_no += 1

                if data == 'QUIT':
                    break
            except socket.timeout:
                print ("Keine Daten")
                continue
        sock.close()
        self._scanner_status.value = "Aufnahme gestoppt"
        print ("Verbindung getrennt")
