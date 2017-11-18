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
        # self.__master = master
        self.__queue = master.queue
        self.__number = nummer
        self.__root = master.root
        self.__go_on_transform = master.go_on_transform
        self.__conf = master.conf

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
        print("SIGINT vdTransformer")

    def run(self):
        """ starts transforming process """
        signal.signal(signal.SIGINT, self.__signal_handler)

        if self.__root:
            os.nice(-15)
        # Erzeugen einer TXT-Datei pro Prozess

        old_folder = ""
        # Dauerschleife

        try:
            while self.__go_on_transform.value:
                try:
                    # Dateinummer aus Warteschleife abfragen und oeffnen
                    filename = self.__queue.get(True, 2)
                    folder = os.path.dirname(filename)
                    if dir != old_folder:
                        vd_file = VdTxtFile(
                            self.__conf,
                            folder + "/vd_file" + str(self.__number))
                        old_folder = folder

                    f = open(filename, "rb")

                    # Anzahl an Datensaetzen in Datei pruefen
                    file_size = os.path.getsize(f.name)
                    dataset_cnt = int(file_size / 1206)

                    for i in range(dataset_cnt):
                        # naechsten Datensatz lesen
                        vd_data = VdDataset(self.__conf, f.read(1206))

                        # Daten konvertieren und speichern
                        vd_data.convert_data()

                        # Datensatz zu Datei hinzufuegen
                        vd_file.add_dataset(vd_data)

                    # Datei schreiben
                    vd_file.write()
                    # Txt-Datei schliessen
                    f.close()
                    # Bin-Datei ggf. loeschen
                    if self.__conf.get("Datei", "binNachTransLoeschen"):
                        os.remove(f.name)
                except Empty:
                    print("Warteschlange leer!")
                    continue
        except BrokenPipeError:
            print("vdTransformer-Pipe defekt")
