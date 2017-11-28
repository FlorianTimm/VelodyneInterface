#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.27
"""

from vdFile import VdFile
from vdPoint import VdPoint

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
