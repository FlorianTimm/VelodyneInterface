#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.20
"""

import json

from vdPoint import VdPoint


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

        self.__vertical_angle = json.loads(
            self.__conf.get("device", "verticalAngle"))
        self.__offset = json.loads(self.__conf.get("device", "offset"))
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
        # change byte order
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
        checks whether dual return is activated
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

        # create empty lists
        azimuths = [0.] * 24
        rotation = [0.] * 12

        # read existing azimuth values
        for j in range(0, 24, 2):
            a = self.get_azimuth(j // 2)
            azimuths[j] = a

        #: rotation angle
        d = 0

        # DualReturn active?
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

        # last rotation angle from angle before
        rotation[11] = d
        azimuths[23] = azimuths[22] + d

        # >360 -> -360
        for j in range(24):
            if azimuths[j] > 360.0:
                azimuths[j] -= 360.0

        # print (azimuths)
        # print (rotation)
        return azimuths, rotation

    def convert_data(self):
        """ converts binary data to objects """

        azimuth, rotation = self.get_azimuths()
        dual_return = self.is_dual_return()

        # timestamp from dataset
        time = self.get_time()
        times = [0.] * 12
        t_2repeat = 2 * float(self.__conf.get("device", "tRepeat"))
        if dual_return:
            for i in range(0,12,2):
                times[i] = time
                times[i+1] = time
                time += t_2repeat
        else:
            for i in range(12):
                times[i] = time
                time += t_2repeat

        t_between_laser = float(self.__conf.get("device", "tInterBeams"))
        t_recharge = float(self.__conf.get("device", "tRecharge"))
        part_rotation = float(self.__conf.get("device", "ratioRotation"))

        # data package has 12 blocks with 32 measurements
        for i in range(12):
            offset = self.__offset[i]
            time = times[i]
            for j in range(2):
                azi_block = azimuth[i*2 + j]
                for k in range(16):
                    # get distance
                    dist = ord(self.__dataset[4 + offset:5 + offset]) \
                        + (ord(self.__dataset[5 + offset:6 + offset]) << 8)
                    if dist > 0:
                        dist /= 500.0

                        reflection = ord(self.__dataset[6 + offset:7 + offset])

                        # interpolate azimuth
                        a = azi_block + rotation[i] * k * part_rotation
                        # print(a)

                        # create point
                        p = VdPoint(
                            self.__conf, round(
                                time, 1), a, self.__vertical_angle[k],
                            dist, reflection)
                        self.__data.append(p)

                    time += t_between_laser

                    # offset for next loop
                    offset += 3
                time += t_recharge - t_between_laser

    def get_data(self):
        """
        get all point data
        :return: list of VdPoints
        :rtype: list
        """
        return self.__data
