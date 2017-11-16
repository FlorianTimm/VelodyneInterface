#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.10.22
'''
from vdPoint import VdPoint
from vdFile import VdFile
import configparser


class ConvTxt2Obj:

    def __init__(self):
        self.fileName = "test.txt"

    def run(self):
        data = []
        conf = configparser.ConfigParser()
        conf.read("config.ini")
        txt = open(self.fileName, 'rb')
        f = VdFile(conf,"obj", self.fileName)
        for line in txt:
            l = line.split()
            data.append(VdPoint(float(l[0]), float(l[1]), float(l[2]),
                                float(l[3]), int(l[4])))
            # print ("test")
            if len(data) > 50000:
                f.writeDataToObj(data)
                data = []
        

if __name__ == '__main__':
    ConvTxt2Obj().run()
