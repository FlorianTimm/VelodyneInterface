#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.17
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

    def __deg2rad(self, degree):
        return degree * self.__dRho

    def get_yxz(self):
        """
        Gets local coordinates
        :return: local coordinates x, y, z in metres
        :rtype: float, float, float
        """
        beam_center = float(self.__conf.get("Geraet", "beamCenter"))

        # Schraegstrecke zum Strahlenzentrum
        d = self.distance - beam_center

        # Vertikalwinkel in Bogenmass
        v = self.vertical_radians

        # Azimut in Bogenmass
        a = self.azimuth_radians

        # Horizontalstrecke bis Drehpunkt
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