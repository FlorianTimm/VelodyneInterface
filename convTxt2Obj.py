#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.10.22
"""
from vdPoint import VdPoint
from vdFile import VdObjFile
import configparser


class ConvTxt2Obj:

    def __init__(self):
        """ Constructor """
        self.fileName = "BeispielDateien/test.txt"

    def run(self):
        """ starts script """
        data = []
        conf = configparser.ConfigParser()
        conf.read("config.ini")
        txt = open(self.fileName, 'rb')
        f = VdObjFile(conf, self.fileName)
        for line in txt:
            dataline = line.split()
            data.append(
                VdPoint(
                    conf, float(dataline[0]), float(
                        dataline[1]), float(dataline[2]),
                    float(dataline[3]), int(dataline[4])))
            # print ("test")
            if len(data) > 50000:
                f.write_data(data)
                data = []
        f.write_data(data)


if __name__ == '__main__':
    ConvTxt2Obj().run()
