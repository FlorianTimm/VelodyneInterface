#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.17
"""

from vdPoint import VdPoint
import json


class VdDataset(object):

    """ representation of one dataset of velodyne vlp-16 """

    def __init__(self, conf, dataset):
        """
        Constructor
        :param conf: config-file
        :type conf: configparser.ConfigParser
        :param dataset: binary dataset
        :type dataset: bytes
        """

        self.__dataset = dataset
        self.__conf = conf

        self.__vertAngle = json.loads(self.__conf.get("Geraet", "vertAngle"))
        self.__offset = json.loads(self.__conf.get("Geraet", "offset"))
        self.__data = []

    def get_azimuth(self, block):
        """
        gets azimuth of a data block
        :param block: number of data block
        :type block: int
        :return: azimuth
        :rtype: float
        """

        offset = self.__offset[block]
        # Horizontalrichtung zusammensetzen, Bytereihenfolge drehen
        azi = ord(self.__dataset[offset + 2:offset + 3]) + \
            (ord(self.__dataset[offset + 3:offset + 4]) << 8)
        azi /= 100.0
        # print(azi)
        return azi

    def get_time(self):
        """
        gets timestamp of dataset
        :return: timestamp of dataset
        :rtype: int
        """

        time = ord(self.__dataset[1200:1201]) + \
            (ord(self.__dataset[1201:1202]) << 8) + \
            (ord(self.__dataset[1202:1203]) << 16) + \
            (ord(self.__dataset[1203:1204]) << 24)
        # print(time)
        return time

    def is_dual_return(self):
        """
        checks wheater dual return is activated
        :return: dual return active?
        :rtype: bool
        """

        mode = ord(self.__dataset[1204:1205])
        if mode == 57:
            return True
        else:
            return False

    def get_azimuths(self):
        """
        get all azimuths and rotation angles from dataset
        :return: azimuths and rotation angles
        :rtype: list, list
        """

        # Leere Listen erzeugen
        azimuths = [0.] * 24
        rotation = [0.] * 12

        # Explizit uebermittelte Azimut-Werte einlesen
        for j in range(0, 24, 2):
            a = self.get_azimuth(j // 2)
            azimuths[j] = a

        # Drehwinkelvariable initialisieren
        d = 0

        # DualReturn aktiv?
        if self.is_dual_return():
            for j in range(0, 19, 4):
                d2 = azimuths[j + 4] - azimuths[j]
                if d2 < 0:
                    d2 += 360.0
                d = d2 / 2.0
                a = azimuths[j] + d
                azimuths[j + 1] = a
                azimuths[j + 3] = a
                rotation[j // 2] = d
                rotation[j // 2 + 1] = d
            # Zweiten
            rotation[10] = d
            azimuths[21] = azimuths[20] + d

        # Strongest / Last-Return
        else:
            for j in range(0, 22, 2):
                d2 = azimuths[j + 2] - azimuths[j]
                if d2 < 0:
                    d2 += 360.0
                d = d2 / 2.0
                a = azimuths[j] + d
                azimuths[j + 1] = a
                rotation[j // 2] = d

        # letzter Drehwinkel wird immer vom vorherigen uebernommen,
        # letzte Horizontalrichtung ergibt sich aus diesem
        rotation[11] = d
        azimuths[23] = azimuths[22] + d

        # Auf Werte ueber 360 Grad pruefen
        for j in range(24):
            if azimuths[j] > 360.0:
                azimuths[j] -= 360.0

        # print (azimuths)
        # print (rotation)
        return azimuths, rotation

    def convert_data(self):
        """ converts binary data to objects """

        # Zeitstempel aus den Daten auslesen
        zeit = self.get_time()

        # Richtung und Drehwinkel auslesen
        azimuth, rotation = self.get_azimuths()

        dual_return = self.is_dual_return()
        t_between_laser = float(self.__conf.get("Geraet", "tZwischenStrahl"))
        t_recharge = float(self.__conf.get("Geraet", "tNachlade"))
        part_rotation = float(self.__conf.get("Geraet", "antDrehung"))

        # Datenpaket besteht aus 12 Bloecken aus jeweils 32 Messergebnissen
        for i in range(12):
            offset = self.__offset[i]
            for j in range(2):
                azi_block = azimuth[i + j]
                for k in range(16):
                    # Entfernung zusammensetzen
                    dist = ord(self.__dataset[4 + offset:5 + offset]) \
                        + (ord(self.__dataset[5 + offset:6 + offset]) << 8)
                    dist /= 500.0

                    # Reflektivitaet auslesen
                    refl = ord(self.__dataset[6 + offset:7 + offset])

                    # Offset in Daten fuer den naechsten Durchlauf
                    offset += 3

                    # Horizontalwinkel interpolieren
                    a = azi_block + rotation[i] * k * part_rotation

                    # a += zeit / 1000000 * 0.1

                    # Punkt erzeugen und anhaengen
                    p = VdPoint(
                        self.__conf, round(zeit, 1), a, self.__vertAngle[k],
                        dist, refl)
                    self.__data.append(p)
                    zeit += t_between_laser

                if dual_return and j == 0:
                    zeit -= t_between_laser * 16
                else:
                    zeit += t_recharge

    def get_data(self):
        """
        get all point data
        :return: list of VdPoints
        :rtype: list
        """
        return self.__data
