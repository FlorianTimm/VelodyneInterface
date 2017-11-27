#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.22
"""

import datetime
import sqlite3
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


class VdASCIIFile(VdFile):
    """ abstract class for writing ascii files """

    def _open_ascii(self, filename, file_format):
        """
        opens ascii file for writing
        :param filename: file name
        :type filename: str
        """
        filename = self._make_filename(file_format, filename)
        self.__file = open(filename, 'a')

    def _write2file(self, data):
        """
        writes ascii data to file
        :param data: data to write
        :type data: str
        """
        self.__file.write(data)

    def write(self):
        """ writes data to file """
        txt = ""
        for d in self.writing_queue:
            txt += self._format(d)
        self._write2file(txt)
        self.clear_writing_queue()

    @abstractmethod
    def _format(self, p):
        """
        abstract method: should convert point data to string for ascii file
        :param p: Point
        :type p: VdPoint
        :return: point data as string
        :rtype: str
        """
        pass

    def close(self):
        """ close file """
        self.__file.close()


class VdObjFile(VdASCIIFile):

    """ creates and fills an obj-file """

    def _open(self, filename=""):
        """
        opens a txt file for writing
        :param filename: name and path to new file
        :type filename: str
        """
        VdASCIIFile._open_ascii(self, filename, "obj")

    def _format(self, p):
        """
        Formats point for OBJ
        :param p: VdPoint
        :type p: VdPoint
        :return: obj point string
        :rtype: str
        """
        x, y, z = p.get_xyz()
        format_string = 'v {:.3f} {:.3f} {:.3f}\n'
        return format_string.format(x, y, z)


class VdXYZFile(VdASCIIFile):

    """ creates and fills an xyz-file """

    def _open(self, filename=""):
        """
        opens a txt file for writing
        :param filename: name and path to new file
        :type filename: str
        """
        VdASCIIFile._open_ascii(self, filename, "xyz")

    def _format(self, p):
        """
        Formats point for OBJ
        :param p: VdPoint
        :type p: VdPoint
        :return: obj point string
        :rtype: str
        """
        x, y, z = p.get_xyz()
        format_string = '{:.3f} {:.3f} {:.3f}\n'
        return format_string.format(x, y, z)


class VdTxtFile(VdASCIIFile):

    """ creates and fills an txt-file """

    def _open(self, filename=""):
        """
        opens a txt file for writing
        :param filename: name and path to new file
        :type filename: str
        """
        VdASCIIFile._open_ascii(self, filename, "txt")

    def _format(self, p):
        """
        Formats point for TXT
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


class VdSQLite(VdFile):
    """ class for writing data to sqlite database """

    def _open(self, filename):
        """
        opens a new db file
        :param filename: name of db file
        :type filename: str
        """
        filename = self._make_filename("db", filename)
        print(filename)
        self.__db = sqlite3.connect(filename)
        self.__cursor = self.__db.cursor()
        self.__cursor.execute("CREATE TABLE raw_data ("
                              "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                              "time FLOAT,"
                              "azimuth FLOAT,"
                              "vertical FLOAT,"
                              "distance FLOAT,"
                              "reflection INTEGER)")
        self.__db.commit()

    def write(self):
        """ writes data to database """
        insert = []
        for p in self.writing_queue:
            insert.append((p.time, p.azimuth, p.vertical,
                           p.distance, p.reflection))

        self.__cursor.executemany("INSERT INTO raw_data ("
                                  "time, azimuth, vertical, "
                                  "distance, reflection) "
                                  "VALUES (?, ?, ?, ?, ?)", insert)
        self.__db.commit()
        self.clear_writing_queue()

    def close(self):
        """ close database """
        self.__db.close()