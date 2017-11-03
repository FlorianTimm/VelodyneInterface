#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.02
'''

class VdConfig(object):
    '''
    Einstellungen des Skriptes
    '''
    
    #IP- und Porteinstellungen
    UDP_IP = '0.0.0.0'  # Net Address
    UDP_PORT_DATA = 2368
    UDP_PORT_GNSS = 8308     # Port
    
    # Zeitgleiche Transformation zu txt aktivieren
    activateTransformer = True
    
    # Vor Aufzeichnung auf GPS warten
    aufGNSSwarten = False
    
    # Binaere Dateien nach deren Transformation loeschen
    binNachTransLoeschen = True
    
    
    ## Geraetekonstanten
    # Zeit zwischen den Messungen der Einzelstrahlen
    tZwischenStrahl = 2.304
    
    # Zeit zwischen zwei Aussendungen des gleichen Messlasers
    tRepeat = 55.296

    # Hoehenwinkel der 16 Messstrahlen
    vertAngle = [-15, 1, -13, -3, -11, 5, -9, 7, -7, 9, -5, 11, -3, 13, -1, 15]

    # Bytes pro Messdatenblock
    offsetBlock = 3 * 32 + 4
    # Versatz vom Start fuer jeden Messblock
    offset = list(range(0,1206,offsetBlock))[0:12]
    
    # Anteil der Zeit zwischen Einzellasern an Widerholungszeit,
    #   fuer Interpolation des Horizontalwinkels
    antDrehung = tZwischenStrahl / tRepeat

    # Zeit nach letztem Strahl bis zum naechsten
    tNachlade = tRepeat - 15 * tZwischenStrahl

    # Dateipraefix der zu speichernden Datei
    fileNamePre = 'data'
    
    # Format der Zeit am Dateinamen
    fileTimeFormat = '%Y-%m-%dT%H:%M:%S'
    
    # Abstand des Strahlenzentrums von der Drehachse
    beamCenter = 0.04191
    
    @staticmethod
    def fileFormatTXT (zeit, azimut, vertikal, distanz, reflexion):
        ''' Einstellung fuer das Erzeugen der TXT-Datei'''
        azimut = round(azimut, 3)
        distanz = round(distanz, 3)
        formatS = '{}\t{}\t{}\t{}\t{}\n'
        return formatS.format(zeit, azimut, vertikal, distanz, reflexion)
