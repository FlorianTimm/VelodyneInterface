#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.19
"""

import datetime

from vdPoint import VdPoint


class VdFile(object):

    """ creates and fills an ascii-file with point data """

    def __init__(self, conf, filename="", file_format="txt"):
        """
        Creates a new ascii-file
        :param conf: configuration file
        :type conf: configparser.ConfigParser
        :param filename: name and path to new file
        :type filename: str
        :param file_format: file suffix, default="txt"
        :type file_format: str
        """
        self.__conf = conf
        # create filename, if not set
        if filename == "":
            filename = self.__make_filename(file_format)
        elif not filename.endswith("." + file_format):
            filename += "." + file_format
        # create file
        self.__file = open(filename, 'a')
        self.__writing_queue = []

    def __get_writing_queue(self):
        """
        Returns points in queue
        :return: points in queue
        :rtype: VdPoint[]
        """
        return self.__writing_queue

    writing_queue = property(__get_writing_queue)

    def clear_writing_queue(self):
        """ clears writing queue """
        self.__writing_queue = []

    def __make_filename(self, file_format):
        """
        generates a new filename from timestamp
        :param file_format: file suffix
        :type file_format: str
        :return: string with date and suffix
        :rtype: str
        """
        #
        filename = self.__conf.get("file", "namePre")
        filename += datetime.datetime.now().strftime(
            self.__conf.get("file", "timeFormat"))
        filename = "." + file_format
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
        for d in self.writing_queue:
            if d.distance > 0.0:
                txt += self.__format(d)
        self._write2file(txt)
        self.clear_writing_queue()

    def __format(self, p):
        raise NotImplementedError("not implemented, use child classes")

    def add_point(self, p):
        """
        Adds a point to write queue
        :param p: point
        :type p: VdPoint
        """
        self.__writing_queue.append(p)

    def add_dataset(self, dataset):
        """
        adds multiple points to write queue
        :param dataset: multiple points
        :type dataset: VdPoint[]
        """
        self.__writing_queue.extend(dataset)

    def read_from_txt_file(self, filename, write=False):
        """
        Parses data from txt file
        :param filename: path and filename of txt file
        :type filename: str
        :param write: write data to new file while reading txt
        :type write: bool
        """
        txt = open(filename)

        for no, line in enumerate(txt):
            try:
                p = VdPoint.parse_string(self.__conf, line)
                self.writing_queue.append(p)
                print("Line {0} was parsed".format(no + 1))
            except ValueError as e:
                print("Error in line {0}: {1}".format(no + 1, e))

            if write and len(self.writing_queue > 50000):
                self.write()
        if write:
            self.write()

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

    def __format(self, p):
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
        VdFile.__init__(self, conf, filename)

    def __format(self, p):
        """
        __format point for TXT
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
