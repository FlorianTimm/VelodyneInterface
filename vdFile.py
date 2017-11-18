#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.18
"""

import datetime


class VdFile(object):

    """
    creates and fills an ascii-file with point data
    """

    def __init__(self, conf, filename="", fileformat="txt"):
        """
        Creates a new ascii-file
        :param conf: configuration file
        :type conf: configparser.ConfigParser
        :param filename: name and path to new file
        :type filename: str
        :param fileformat: file suffix, default="txt"
        :type fileformat: str
        """
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
        """
        generates a new filename from timestamp
        :param fileformat: file suffix
        :type fileformat: str
        :return: string with date and suffix
        :rtype: str
        """
        # Jahr-Monat-TagTStunde:Minute:Sekunde an Dateinamen anhaengen
        filename = self._conf.get("Datei", "fileNamePre")
        filename += datetime.datetime.now().strftime(
            self._conf.get("Datei", "fileTimeFormat"))
        filename = "." + fileformat
        return filename

    def _write2file(self, data):
        """
        writes ascii data to file
        :param data: data to write
        :type data: str
        """
        self._file.write(data)

    def write_data(self, data):
        """
        adds data and writes it to file
        :param data: ascii data to write
        :type data: VdPoint[]
        """
        self.add_dataset(data)
        self.write()

    def write(self):
        """
        writes data, will be implemented by child class
        """
        print("not implemented - use VdObjFile or VdTxtFile instead")

    def add_point(self, p):
        """
        Adds a point to write queue
        :param p: point
        :type p: VdPoint
        """
        self._data.append(p)

    def add_dataset(self, dataset):
        """
        adds multiple points to write queue
        :param dataset: multiple points
        :type dataset: VdPoint[]
        """
        self._data.extend(dataset)

    def close(self):
        """ close file """
        self._file.close()


class VdObjFile(VdFile):

    """ creates and fills an obj-file """

    def __init__(self, conf, filename=""):
        """
        Creates a new obj-file
        :param conf: configuration file
        :type conf: configparser.ConfigParser
        :param filename: name and path to new file
        :type filename: str
        """
        VdFile.__init__(self, conf, filename, "obj")

    def write(self):
        """writes data to file """
        obj = ""

        for p in self._data:
            if p.get_distance() > 0.0:
                x, y, z = p.get_yxz()
                format_string = 'v {:.3f} {:.3f} {:.3f}\n'
                obj += format_string.format(x, y, z)
        self._write2file(obj)
        self._data = []


class VdTxtFile(VdFile):

    """ creates and fills an txt-file """

    def __init__(self, conf, filename=""):
        """
        Creates a new txt-file
        :param conf: configuration file
        :type conf: configparser.ConfigParser
        :param filename: name and path to new file
        :type filename: str
        """
        VdFile.__init__(self, conf, filename, "txt")

    def write(self):
        """writes data to file """
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
    def _fileformat_txt(time, azimuth, vertical, distance, reflexion):
        """
        Formats point data
        :param time: recording time in microseconds
        :type time: int
        :param azimuth: Azimuth direction in degrees
        :type azimuth: float
        :param vertical: Vertical angle in degrees
        :type vertical: float
        :param distance: distance in metres
        :type distance: float
        :param reflexion: reflexion 0-255
        :type reflexion: int
        """
        format_string = '{:012.1f}\t{:07.3f}\t{: 03.0f}\t{:06.3f}\t{:03.0f}\n'
        return format_string.format(time,
                                    azimuth,
                                    vertical,
                                    distance,
                                    reflexion)
