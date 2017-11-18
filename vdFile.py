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
        self.__conf = conf
        # Dateiname erzeugen, sofern kein Dateiname mitgeliefert
        if filename == "":
            filename = self.__make_filename(fileformat)
        elif not filename.endswith("." + fileformat):
            filename += "." + fileformat
        # Datei erzeugen
        self.__file = open(filename, 'a')
        self.__write_queue = []

    def __get_write_queue(self):
        """
        Returns points in queue
        :return: points in queue
        :rtype: VdPoint[]
        """
        return self.__write_queue
    write_queue = property(__get_write_queue)

    def clear_write_queue(self):
        self.__write_queue = []

    def __make_filename(self, fileformat):
        """
        generates a new filename from timestamp
        :param fileformat: file suffix
        :type fileformat: str
        :return: string with date and suffix
        :rtype: str
        """
        # Jahr-Monat-TagTStunde:Minute:Sekunde an Dateinamen anhaengen
        filename = self.__conf.get("Datei", "fileNamePre")
        filename += datetime.datetime.now().strftime(
            self.__conf.get("Datei", "fileTimeFormat"))
        filename = "." + fileformat
        return filename

    def _write2file(self, data):
        """
        writes ascii data to file
        :param data: data to write
        :type data: str
        """
        self.__file.write(data)

    def write_data(self, data):
        """
        adds data and writes it to file
        :param data: ascii data to write
        :type data: VdPoint[]
        """
        self.add_dataset(data)
        self.write()

    def write(self):
        """writes data to file """
        txt = ""
        for d in self.write_queue:
            if d.distance > 0.0:
                txt += self.format(d)
        self._write2file(txt)
        self.clear_write_queue()

    def format(self, p):
        print("not implemented")

    def add_point(self, p):
        """
        Adds a point to write queue
        :param p: point
        :type p: VdPoint
        """
        self.__write_queue.append(p)

    def add_dataset(self, dataset):
        """
        adds multiple points to write queue
        :param dataset: multiple points
        :type dataset: VdPoint[]
        """
        self.__write_queue.extend(dataset)

    def close(self):
        """ close file """
        self.__file.close()


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

    def format(self, p):
        """
        Format point for OBJ
        :param p: VdPoint
        :type p: VdPoint
        :return: obj point string
        :rtype: str
        """
        x, y, z = p.get_yxz()
        format_string = 'v {:.3f} {:.3f} {:.3f}\n'
        return format_string.format(x, y, z)

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

    def format(self, p):
        """
        format point for TXT
        :param p: VdPoint
        :type p: VdPoint
        :return: txt point string
        :rtype: str
        """
        format_string = '{:012.1f}\t{:07.3f}\t{: 03.0f}\t{:06.3f}\t{:03.0f}\n'
        return format_string.format(p.time,
                                    p.azimuth,
                                    p.vertical,
                                    p.distance,
                                    p.reflection)
