#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.17
"""

import math


class VdPoint(object):

    """ Represents a point """
    _dRho = math.pi / 180.0

    def __init__(self, conf, time, azimuth, vertical, distance, reflexion):
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
        :param reflexion: reflexion 0-255
        :type reflexion: int
        """
        self._time = time
        self._azimuth = azimuth
        self._vertical = vertical
        self._reflection = reflexion
        self._distance = distance
        self._conf = conf

    def _deg2rad(self, degree):
        return degree * self._dRho

    def get_time(self):
        """
        Gets recording time
        :return: recording time in microseconds
        :rtype: float
        """
        return self._time

    def get_azimuth(self):
        """
        Gets azimuth direction
        :return: azimuth direction in degrees
        :rtype: float
        """
        return self._azimuth

    def get_azimuth_radians(self):
        """
        Gets azimuth in radians
        :return: azimuth direction in radians
        :rtype: float
        """
        return self._deg2rad(self.get_azimuth())

    def get_vertical(self):
        """
        Gets vertical angle in degrees
        :return: vertical angle in degrees
        :rtype: float
        """
        return self._vertical

    def get_vertical_radians(self):
        """
        Gets vertical angle in radians
        :return: vertical angle in radians
        :rtype: float
        """
        return self._deg2rad(self.get_vertical())

    def get_reflection(self):
        """
        Gets reflexion
        :return: reflexion between 0 and 255
        :rtype: int
        """
        return self._reflection

    def get_distance(self):
        """
        Gets distance
        :return: distance in metres
        :rtype: float
        """
        return self._distance

    def get_yxz(self):
        """
        Gets local coordinates
        :return: local coordinates x, y, z in metres
        :rtype: float, float, float
        """
        beam_center = float(self._conf.get("Geraet", "beamCenter"))

        # Schraegstrecke zum Strahlenzentrum
        d = self.get_distance() - beam_center

        # Vertikalwinkel in Bogenmass
        v = self.get_vertical_radians()

        # Azimut in Bogenmass
        a = self.get_azimuth_radians()

        # Horizontalstrecke bis Drehpunkt
        s = d * math.cos(v) + beam_center

        x = s * math.sin(a)
        y = s * math.cos(a)
        z = d * math.sin(v)

        return x, y, z
