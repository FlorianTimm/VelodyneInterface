#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.12
'''

from vdBuffer import VdBuffer
from vdInterface import VdInterface
from vdConfig import VdConfig
from vdTransformer import VdTransformer
import time

from datetime import datetime
from multiprocessing import Queue, Manager
import multiprocessing
from threading import Thread
from flask import Flask
import os

# Pruefen, ob es sich um einen Raspberry handelt
try:
    import RPi.GPIO as GPIO
    raspberry = True
except ModuleNotFoundError as mne:
    raspberry = False
    


class VdAutoStart(object):
    '''
    Startskript
    '''
    #buffer = None

    def __init__(self):
        '''
        Constructor
        '''
        print("Datenschnittstelle fuer VLP-16\n")    
        
        if VdConfig.activateTransformer:
            # Liste fuer Transformerprozesse
            self.transformer= []
            # Warteschlange fuer Transformer
            self.warteschlange = Queue()
        
        # Pipes fuer Prozesskommunikation erzeugen
        manager = Manager()
        self.gnssStatus = "unbekannt"
        #self.gnssReady = manager.Value('gnssReady',False)
        self.noBreak = manager.Value('noBreak', False)
        self.scannerStatus = manager.Value('scannerStatus', "unbekannt")
        self.datensaetze = manager.Value('datensaetze', 0)
        self.date = manager.Value('date', datetime.now())

        # pruefe, ob root-Rechte vorhanden sind
        try:
            os.rename('/etc/foo', '/etc/bar')
            self.admin = True
        except IOError as e:
            self.admin = False
        
    def run(self):
        ''' Starte das Programm '''
        
        if raspberry:
            print ("Raspberry Pi wurde erkannt")
            # Hardwaresteuerung starten
            from vdHardware import VdHardware
            vdH = VdHardware(self)
            vdH.start()
        else:
            print ("Raspberry Pi wurde nicht erkannt")
            print ("Hardwaresteuerung wurde deaktiviert")
            
            
        # Zeit gemaess GNSS einstellen
        if VdConfig.aufGNSSwarten:
            print ("Warte auf GNSS-Signal...")
            VdInterface.getGNSSTime(ms)
        

         
        # Transformerprozess gemaess Prozessoranzahl
        if VdConfig.activateTransformer:
            n = multiprocessing.cpu_count() - 1
            if n < 2:
                n = 1
            self.pTransformer = []
            for i in range (n):
                t = VdTransformer(self.warteschlange, i, self.admin)
                t.start()
                self.pTransformer.append(t)
    
    def aufzeichnungStarten (self):
        if not(self.noBreak.value and self.pBuffer.is_alive()): 
            self.noBreak.value = True
            print("Aufzeichnung wird gestartet...")
            self.scannerStatus.value = "Aufnahme gestartet"
            # Speicherprozess starten
            self.pBuffer = VdBuffer(self.noBreak,self.scannerStatus,
                self.datensaetze, self.warteschlange, self.admin, self.date);
            self.pBuffer.start()
    
    def aufzeichnungStoppen (self):
        if self.noBreak.value and self.pBuffer.is_alive():
            self.noBreak.value = False
            print("Aufzeichnung wird innerhalb von 5 Sekunden gestoppt")
            time.sleep(5)
            self.pBuffer.terminate()
            self.scannerStatus.value = "Aufnahme gestoppt"
            del (self.pBuffer)
            
    def transformerStoppen (self):
        for t in self.pTransformer:
            t.terminate()
            
    def herunterFahren(self):
        self.aufzeichnungStoppen();
        self.transformerStoppen()
        os.system("sudo shutdown -h now")
        print ("Faehrt herunter")
# Websteuerung
app = Flask(__name__)


@app.route("/")
def webIndex():
    timediff = datetime.now()-ms.date.value
    laufzeit = str(timediff.seconds + (int(timediff.microseconds/1000)/1000.))
    ausgabe = """<html>
    <head>
        <title>VLP16-Datenschnittstelle</title>
        <style>
            table {
                border-collapse: collapse;
            }
            td {
                border: 1px solid black;
            }
        </style>
        <meta http-equiv="refresh" content="10; URL=/">
    </head>
    <body>
        <h2>VLP16-Datenschnittstelle</h3>
        <table style="">
            <tr><td>GNSS-Status:</td><td>"""+ms.gnssStatus+"""</td></tr>
            <tr><td>Scanner:</td><td>"""+ms.scannerStatus.value+"""</td></tr>
            <tr><td>Datensaetze:</td>
                <td>"""+str(ms.datensaetze.value)+"""</td></tr>
            <tr><td>Warteschleife:</td>
                <td>"""+str(ms.warteschlange.qsize())+"""</td></tr>
            <tr><td>Laufzeit</td>
                <td>"""+laufzeit+"""</td></tr>"""
    if ms.noBreak.value and ms.pBuffer.is_alive():
        ausgabe += """<tr><td colspan="2">
                <a href="/stoppen">Aufzeichnung stoppen</a></td></tr>"""
    else:
        ausgabe += """<tr><td colspan="2">
                <a href="/starten">Aufzeichnung starten</a></td></tr>"""  
    ausgabe += """<tr><td colspan="2">
                <a href="/shutdown">Raspberry herunterfahren</a></td></tr>
            </tr>
        </table>
    </body>
    </html>"""
    
    return ausgabe
        
@app.route("/shutdown")
def webShutdown():
    ms.herunterFahren()
    return """
    <meta http-equiv="refresh" content="5; URL=/">
    Wird in 10 Sekunden heruntergefahren..."""

@app.route("/stoppen")
def webStoppen():
    ms.aufzeichnungStoppen()
    return """
    <meta http-equiv="refresh" content="5; URL=/">
    Aufzeichnung wird gestoppt..."""

@app.route("/starten")
def webStarten():
    ms.aufzeichnungStarten()
    return """
    <meta http-equiv="refresh" content="5; URL=/">
    Aufzeichnung wird gestartet..."""

def startWeb():
    print("Webserver startet...")
    app.run('0.0.0.0', 8080)
    
if __name__ == '__main__':
    ms = VdAutoStart()
    t = Thread(target=startWeb)
    t.start()
    ms.run()
    
