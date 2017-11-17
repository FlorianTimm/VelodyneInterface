#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.17
"""

import datetime


class VdFile(object):

    def __init__(self, conf, filename="", fileformat="txt"):
        self._conf = conf
        # Dateiname erzeugen, sofern kein Dateiname mitgeliefert
        if filename == "":
            filename = self._make_filename(fileformat)
        elif not filename.endswith("." + fileformat):
            filename += "." + fileformat
        # Datei erzeugen
        self._file = open(filename, 'a')
        self._data = []

    def _make_filename(self, fileformat):
        # Jahr-Monat-TagTStunde:Minute:Sekunde an Dateinamen anhaengen
        filename = self._conf.get("Datei", "fileNamePre")
        filename += datetime.datetime.now().strftime(
            self._conf.get("Datei", "fileTimeFormat"))
        filename = "." + fileformat
        return filename

    def _write2file(self, data):
        """ Daten in Datei schreiben """
        self._file.write(data)

    def write_data(self, data):
        self.add_dataset(data)
        self.write()

    def write(self):
        print("nicht implementiert")

    def add_point(self, p):
        self._data.append(p)

    def add_dataset(self, dataset):
        self._data.extend(dataset)

    def close(self):
        """ Datei schliessen """
        self._file.close()


class VdObjFile(VdFile):

    def __init__(self, conf, filename=""):
        VdFile.__init__(self, conf, filename, "obj")

    def write(self):
        obj = ""

        for p in self._data:
            if p.get_distance() > 0.0:
                x, y, z = p.get_yxz()
                format_string = 'v {:.3f} {:.3f} {:.3f}\n'
                obj += format_string.format(x, y, z)
        self._write2file(obj)
        self._data = []


class VdTxtFile(VdFile):

    def __init__(self, conf, filename=""):
        VdFile.__init__(self, conf, filename, "txt")

    def write(self):
        txt = ""
        for d in self._data:
            if d.get_distance() > 0.0:
                txt += self._fileformat_txt(d.get_time(),
                                            d.get_azimuth(),
                                            d.get_vertical(),
                                            d.get_distance(),
                                            d.get_reflection())
        self._write2file(txt)
        self._data = []

    @staticmethod
    def _fileformat_txt(zeit, azimut, vertikal, distanz, reflexion):
        """ Einstellung fuer das Erzeugen der TXT-Datei"""
        format_string = '{:012.1f}\t{:07.3f}\t{: 03.0f}\t{:06.3f}\t{:03.0f}\n'
        return format_string.format(zeit,
                                    azimut,
                                    vertikal,
                                    distanz,
                                    reflexion)
