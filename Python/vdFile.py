#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.27
"""

import datetime
from abc import abstractmethod, ABC

from vdPoint import VdPoint


class VdFile(ABC):

    """ abstract class for saving data """

    def __init__(self, conf, filename=""):
        """
        Creates a new ascii-file
        :param conf: configuration file
        :type conf: configparser.ConfigParser
        :param filename: name and path to new file
        :type filename: str
        """
        self.__conf = conf
        # create file
        self.__writing_queue = []
        self._open(filename)

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

    def _make_filename(self, file_format, file_name=""):
        """
        generates a new file_name from timestamp
        :param file_format: file suffix
        :type file_format: str
        :return: string with date and suffix
        :rtype: str
        """
        if file_name == "":
            name = self.__conf.get("file", "namePre")
            name += datetime.datetime.now().strftime(
                self.__conf.get("file", "timeFormat"))
            name = "." + file_format
            return name
        elif not file_name.endswith("." + file_format):
            return file_name + "." + file_format
        return file_name

    def write_data(self, data):
        """
        adds data and writes it to file
        :param data: ascii data to write
        :type data: VdPoint[]
        """
        self.add_dataset(data)
        self.write()

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
                # print("Line {0} was parsed".format(no + 1))
            except ValueError as e:
                print("Error in line {0}: {1}".format(no + 1, e))

            if write and len(self.writing_queue) > 50000:
                self.write()
        if write:
            self.write()

    @abstractmethod
    def write(self):
        """ abstract method: should write data from writing_queue """
        pass

    @abstractmethod
    def _open(self, filename):
        """
        abstract method: should open file for writing
        :param filename: file name
        :type filename: str
        """
        pass

    @abstractmethod
    def close(self):
        """ abstract method: should close file """
        pass
