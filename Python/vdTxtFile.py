#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.27
"""

from vdASCIIFile import VdASCIIFile
from vdPoint import VdPoint


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
        format_string = '{:012.1f}\t{:07.3f}\t{:03.0f}\t{:06.3f}\t{:03.0f}\n'
        return format_string.format(p.time,
                                    p.azimuth,
                                    p.vertical,
                                    p.distance,
                                    p.reflection)
