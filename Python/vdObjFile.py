#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.27
"""

from vdASCIIFile import VdASCIIFile
from vdPoint import VdPoint


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
