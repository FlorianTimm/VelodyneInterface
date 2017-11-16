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
import signal


class VdTransformer(Process):

    """
    Erzeugt einen Prozess zum Umwandeln von binaeren Daten des
    Velodyne VLP-16 zu TXT-Dateien
    """

    def __init__(self, nummer, masterSkript):
        """
        Konstruktor fuer Transformer-Prozess, erbt von multiprocessing.Process

        Parameters
        ----------
        masterSkript : VdAutoStart
            Objekt des Hauptskriptes
        """

        # Konstruktor der Elternklasse
        Process.__init__(self)

        # Parameter sichern
        self._masterSkript = masterSkript
        self._warteschlange = masterSkript.warteschlange
        self._nummer = nummer
        self._admin = masterSkript.admin
        self._weiterUmformen = masterSkript.weiterUmformen
        self._conf = masterSkript.conf

    def _signal_handler(self, signal, frame):
        """ Behandelt SIGINT-Signale """
        # self.masterSkript.ende()
        print("SIGINT vdTransformer")

    def run(self):
        """
        Ausfuehrung des Umform-Prozesses,
        laedt Daten aus der Warteschlange von VdAutoStart,
        formt die Daten in Objekte um und speichert diese
        """
        signal.signal(signal.SIGINT, self._signal_handler)

        if self._admin:
            os.nice(-15)
        # Erzeugen einer TXT-Datei pro Prozess

        oldFolder = ""
        # Dauerschleife

        try:
            while self._weiterUmformen.value:
                try:
                    # Dateinummer aus Warteschleife abfragen und oeffnen
                    filename = self._warteschlange.get(True, 2)
                    folder = os.path.dirname(filename)
                    if dir != oldFolder:
                        file = VdFile(
                            self._conf,
                            "txt",
                            folder + "/file" + str(self._nummer))
                        oldFolder = folder

                    f = open(filename, "rb")

                    # Anzahl an Datensaetzen in Datei pruefen
                    fileSize = os.path.getsize(f.name)
                    cntDatasets = int(fileSize / 1206)

                    for i in range(cntDatasets):
                        # naechsten Datensatz lesen
                        vdData = VdDataset(self._conf, f.read(1206))

                        # Daten konvertieren und speichern
                        vdData.convertData()

                        # Datensatz zu Datei hinzufuegen
                        file.addDataset(vdData)

                    # Datei schreiben
                    file.writeTxt()
                    # Txt-Datei schliessen
                    f.close()
                    # Bin-Datei ggf. loeschen
                    if self._conf.get("Datei", "binNachTransLoeschen"):
                        os.remove(f.name)
                except Empty:
                    print ("Warteschlange leer!")
                    continue
        except BrokenPipeError:
            print ("vdTransformer-Pipe defekt")
