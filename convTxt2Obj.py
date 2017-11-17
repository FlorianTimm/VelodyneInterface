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
        self.fileName = "BeispielDateien/test.txt"

    def run(self):
        data = []
        conf = configparser.ConfigParser()
        conf.read("config.ini")
        txt = open(self.fileName, 'rb')
        f = VdObjFile(conf, self.fileName)
        for line in txt:
            daten = line.split()
            data.append(
                VdPoint(
                    conf, float(daten[0]), float(daten[1]), float(daten[2]),
                    float(daten[3]), int(daten[4])))
            # print ("test")
            if len(data) > 50000:
                f.write_data(data)
                data = []
        f.write_data(data)

if __name__ == '__main__':
    ConvTxt2Obj().run()
