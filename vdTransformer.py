#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.17
"""
import os
import signal
from multiprocessing import Process
from queue import Empty
from vdFile import VdTxtFile
from vdDataset import VdDataset


class VdTransformer(Process):

    """
    Erzeugt einen Prozess zum Umwandeln von binaeren Daten des
    Velodyne VLP-16 zu TXT-Dateien
    """

    def __init__(self, nummer, master):
        """
        Konstruktor fuer Transformer-Prozess, erbt von multiprocessing.Process

        Parameters
        ----------
        nummer : int
            Nummer des Transformerprozess
        master : VdAutoStart
            Objekt des Hauptskriptes
        """

        # Konstruktor der Elternklasse
        Process.__init__(self)

        # Parameter sichern
        # self._master = master
        self._queue = master.get_queue()
        self._number = nummer
        self._root = master.get_root()
        self._go_on_transform = master.get_go_on_transform()
        self._conf = master.get_conf()

    @staticmethod
    def _signal_handler(signal, frame):
        """ Behandelt SIGINT-Signale """
        # self.master.ende()
        print("SIGINT vdTransformer")

    def run(self):
        """
        Ausfuehrung des Umform-Prozesses,
        laedt Daten aus der Warteschlange von VdAutoStart,
        formt die Daten in Objekte um und speichert diese
        """
        signal.signal(signal.SIGINT, self._signal_handler)

        if self._root:
            os.nice(-15)
        # Erzeugen einer TXT-Datei pro Prozess

        old_folder = ""
        # Dauerschleife

        try:
            while self._go_on_transform.value:
                try:
                    # Dateinummer aus Warteschleife abfragen und oeffnen
                    filename = self._queue.get(True, 2)
                    folder = os.path.dirname(filename)
                    if dir != old_folder:
                        vd_file = VdTxtFile(
                            self._conf,
                            folder + "/vd_file" + str(self._number))
                        old_folder = folder

                    f = open(filename, "rb")

                    # Anzahl an Datensaetzen in Datei pruefen
                    file_size = os.path.getsize(f.name)
                    dataset_cnt = int(file_size / 1206)

                    for i in range(dataset_cnt):
                        # naechsten Datensatz lesen
                        vd_data = VdDataset(self._conf, f.read(1206))

                        # Daten konvertieren und speichern
                        vd_data.convert_data()

                        # Datensatz zu Datei hinzufuegen
                        vd_file.add_dataset(vd_data)

                    # Datei schreiben
                    vd_file.write()
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
