#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.17
"""

import math


class VdPoint(object):

    """ Stellt eine Messung da """
    _dRho = math.pi / 180.0

    def __init__(self, conf, zeit, azimut, vertikal, distanz, reflexion):
        self._time = zeit
        self._azimuth = azimut
        self._vertical = vertikal
        self._reflection = reflexion
        self._distance = distanz
        self._conf = conf

    def _deg2rad(self, grad):
        return grad * self._dRho

    def get_time(self):
        """Uebergibt die Aufzeichnungzeit"""
        return self._time

    def get_azimuth(self):
        """Uebergibt die Horizontalrichtung in Grad"""
        return self._azimuth

    def get_azimuth_radians(self):
        """Uebergibt die Horizonalrichung in Bogenmass"""
        return self._deg2rad(self.get_azimuth())

    def get_vertical(self):
        """Uebergibt den Hoehenwinkel in Grad"""
        return self._vertical

    def get_vertical_radians(self):
        """Uebergibt den Hoehenwinkel in Bogenmass"""
        return self._deg2rad(self.get_vertical())

    def get_reflection(self):
        """Uebergibt die Reflexionsstaerke von 0 bis 255"""
        return self._reflection

    def get_distance(self):
        """Uebergibt die gemessene Strecke"""
        return self._distance

    def get_yxz(self):
        """Uebergibt XYZ-Koordinaten"""
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
