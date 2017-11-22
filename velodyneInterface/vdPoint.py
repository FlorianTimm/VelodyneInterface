#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.19
"""

import math


class VdPoint(object):

    """ Represents a point """

    __dRho = math.pi / 180.0

    def __init__(self, conf, time, azimuth, vertical, distance, reflection):
        """
        Constructor
        :param conf: config file
        :type conf: configparser.ConfigParser
        :param time: recording time in microseconds
        :type time: float
        :param azimuth: Azimuth direction in degrees
        :type azimuth: float
        :param vertical: Vertical angle in degrees
        :type vertical: float
        :param distance: distance in metres
        :type distance: float
        :param reflection: reflection 0-255
        :type reflection: int
        """
        self.__time = time
        self.__azimuth = azimuth
        self.__vertical = vertical
        self.__reflection = reflection
        self.__distance = distance
        self.__conf = conf

    @staticmethod
    def parse_string(conf, line):
        """
        Parses string to VdPoint
        :param conf: config file
        :type conf: configparser.ConfigParser
        :param line: Point as TXT
        :type line: str
        :return: Point
        :rtype: VdPoint
        :raise ValueError: malformed string
        """
        d = line.split()
        if len(d) > 4:
            time = float(d[0])
            azimuth = float(d[1])
            vertical = float(d[2])
            distance = float(d[3])
            reflection = int(d[4])
            return VdPoint(conf, time, azimuth,
                           vertical, distance, reflection)
        else:
            raise ValueError('Malformed string')

    def __deg2rad(self, degree):
        """
        converts degree to radians
        :param degree: degrees
        :type degree: float
        :return: radians
        :rtype: float
        """
        return degree * self.__dRho

    def get_xyz(self):
        """
        Gets local coordinates
        :return: local coordinates x, y, z in metres
        :rtype: float, float, float
        """
        beam_center = float(self.__conf.get("device", "beamCenter"))

        # slope distance to beam center
        d = self.distance - beam_center

        # vertical angle in radians
        v = self.vertical_radians

        # azimuth in radians
        a = self.azimuth_radians

        # horizontal distance
        s = d * math.cos(v) + beam_center

        x = s * math.sin(a)
        y = s * math.cos(a)
        z = d * math.sin(v)

        return x, y, z

    def __get_time(self):
        """
        Gets recording time
        :return: recording time in microseconds
        :rtype: float
        """
        return self.__time

    def __get_azimuth(self):
        """
        Gets azimuth direction
        :return: azimuth direction in degrees
        :rtype: float
        """
        return self.__azimuth

    def __get_azimuth_radians(self):
        """
        Gets azimuth in radians
        :return: azimuth direction in radians
        :rtype: float
        """
        return self.__deg2rad(self.azimuth)

    def __get_vertical(self):
        """
        Gets vertical angle in degrees
        :return: vertical angle in degrees
        :rtype: float
        """
        return self.__vertical

    def __get_vertical_radians(self):
        """
        Gets vertical angle in radians
        :return: vertical angle in radians
        :rtype: float
        """
        return self.__deg2rad(self.vertical)

    def __get_reflection(self):
        """
        Gets reflection
        :return: reflection between 0 and 255
        :rtype: int
        """
        return self.__reflection

    def __get_distance(self):
        """
        Gets distance
        :return: distance in metres
        :rtype: float
        """
        return self.__distance

    # properties
    time = property(__get_time)
    azimuth = property(__get_azimuth)
    azimuth_radians = property(__get_azimuth_radians)
    vertical = property(__get_vertical)
    vertical_radians = property(__get_vertical_radians)
    reflection = property(__get_reflection)
    distance = property(__get_distance)
