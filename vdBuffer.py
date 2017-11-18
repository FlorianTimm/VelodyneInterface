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

    """ process for buffering binary data """

    def __init__(self, master):
        """
        Constructor
        :param master: instance of VdAutoStart
        :type master: VdAutoStart
        """
        # Konstruktor der Elternklasse
        Process.__init__(self)

        # Pipes sichern
        # self.__master = master
        self.__go_on_buffering = master.go_on_buffer
        self.__scanner_status = master.scanner_status
        self.__datasets = master.dataset_cnt
        self.__queue = master.queue
        self.__admin = master.root
        self.__date = master.date
        self.__conf = master.conf

        self.__file_no = 0

    @staticmethod
    def __signal_handler(sig_no, frame):
        """
        handles SIGINT-signal
        :param sig_no: signal number
        :type sig_no: int
        :param frame:execution frame
        :type frame: frame
        """
        del sig_no, frame
        # self.master.end()
        print("SIGINT vdBuffer")

    def __new_folder(self):
        """ creates data folder """
        # Uhrzeit abfragen fuer Laufzeitlaenge und Dateinamen
        self.__date.value = datetime.now()
        self.__folder = self.__conf.get("Datei", "fileNamePre")
        self.__folder += self.__date.value.strftime(
            self.__conf.get("Datei", "fileTimeFormat"))
        # Speicherordner anlegen und ausgeben
        os.makedirs(self.__folder)
        print("Data folder: " + self.__folder)

    def run(self):
        """ starts buffering process """
        signal.signal(signal.SIGINT, self.__signal_handler)

        # Socket zum Scanner oeffnen
        sock = VdInterface.get_data_stream(self.__conf)
        self.__scanner_status.value = "Socket verbunden"

        # Variablen initialisieren
        minibuffer = b''
        j = 0

        self.__datasets.value = 0

        # Prozessprioritaet hochschalten, sofern Adminrechte
        if self.__admin:
            os.nice(-18)

        transformer = self.__conf.get("Funktionen", "activateTransformer")
        measurements_per_dataset = int(self.__conf.get(
            "Geraet", "messungProDatensatz"))

        # Dauerschleife, solange kein Unterbrechen-Befehl kommt

        sock.settimeout(1)
        while self.__go_on_buffering.value:
            try:
                # Daten vom Scanner holen
                data = sock.recvfrom(1248)[0]

                if j == 0 and self.__file_no == 0:
                    self.__new_folder()
                # RAM-Buffer
                minibuffer += data
                j += 1
                self.__datasets.value += measurements_per_dataset
                # Alle 5 bzw. 10 Sekunden Daten speichern
                # oder wenn Abbrechenbefehl kommt
                if (j >= 1500) or (not self.__go_on_buffering.value):
                    # Datei schreiben
                    f = open(
                        self.__folder + "/" + str(self.__file_no) + ".bin",
                        "wb")
                    f.write(minibuffer)

                    f.close()

                    if transformer:
                        self.__queue.put(f.name)

                    # Buffer leeren
                    minibuffer = b''
                    j = 0

                    # Dateizaehler
                    self.__file_no += 1

                if data == 'QUIT':
                    break
            except socket.timeout:
                print("No data")
                continue
        sock.close()
        self.__scanner_status.value = "recording stopped"
        print("Disconnected!")
