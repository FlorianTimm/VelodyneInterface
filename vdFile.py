#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.10.27
'''

import datetime
import math


class VdFile(object):  
     
    def __init__ (self, conf, fileType = "txt", fileName = ""):
        self._conf = conf
        
        # Dateiname erzeugen, sofern kein Dateiname mitgeliefert
        if (fileName == ""):
            #Jahr-Monat-TagTStunde:Minute:Sekunde an Dateinamen anhaengen
            fileName =  self._conf.get("Datei","fileNamePre")
            fileName += datetime.datetime.now().strftime(
                self._conf.get("Datei","fileTimeFormat"))
        
        fileName += '.' + fileType
            
        # Datei erzeugen
        self.txtFile = open(fileName, 'a')
        self.datasets = []

    
    def write (self, data):
        ''' Daten in Datei schreiben '''
        self.txtFile.write(data)
        
    def writeDatasetToTxt (self, dataset):
        self.addDataset(dataset)
        self.writeTxt()
        
        
    def writeTxt(self):
        txt = ""
        for ds in self.datasets:
            for d in ds.getData():
                if d.distanz > 0.0:
                    txt += VdFile.fileFormatTXT(d.zeit, 
                                d.azimut, d.vertikal, d.distanz, d.reflexion)
        self.write(txt)
        print("Geschrieben!")
        self.datasets = []
            
    def addDataset(self, dataset):
        self.datasets.append(dataset)        
    
    def writeDataToObj(self, data):
        obj = ""
        for p in data:
            # Schraegstrecke zum Strahlenzentrum
            d = p.distanz - VdConfig.beamCenter
            
            # Vertikalwinkel in Bogenmass
            v = p.vertikal / 180.0 * math.pi
            
            # Azimut in Bogenmass
            a = p.azimut / 180.0 * math.pi
            
            # Z-Komponente
            z = d * math.sin(v)
            
            # Horizontalstrecke bis Drehpunkt
            s = d * math.cos(v) + VdConfig.beamCenter
            
            # X-Komponente
            x = s * math.sin(a)
            
            # Y-Komponente
            y = s * math.cos(a)
            
           
            formatS = 'v {} {} {}\n'
            obj += formatS.format(x,y,z)
        self.write(obj)
                       
    @staticmethod
    def fileFormatTXT (zeit, azimut, vertikal, distanz, reflexion):
        ''' Einstellung fuer das Erzeugen der TXT-Datei'''
        azimut = round(azimut, 3)
        distanz = round(distanz, 3)
        formatS = '{}\t{}\t{}\t{}\t{}\n'
        return formatS.format(zeit, azimut, vertikal, distanz, reflexion)
    
    def close (self):
        ''' Datei schliessen '''
        self.txtFile.close()
