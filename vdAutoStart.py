#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.02
'''

from vdBuffer import VdBuffer
from vdInterface import VdInterface
from vdConfig import VdConfig
from vdTransformer import VdTransformer

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
        self.noBreak = manager.Value('noBreak', True)
        self.scannerStatus = manager.Value('scannerStatus', "unbekannt")
        self.datensaetze = manager.Value('datensaetze', 0)
        
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
        
        # Uhrzeit abfragen fuer Laufzeitlaenge und Dateinamen
        self.date = datetime.now()
        folder = self.date.strftime(VdConfig.fileTimeFormat) 

        # Speicherordner anlegen und ausgeben
        os.makedirs(folder)  
        print ("Speicherordner: " + folder)      
        
        # Speicherprozess starten
        self.pBuffer = VdBuffer(folder, self.noBreak,self.scannerStatus,
                            self.datensaetze, self.warteschlange, self.admin);
        self.pBuffer.start()
         
        # Transformerprozess gemaess Prozessoranzahl
        if VdConfig.activateTransformer:
            n = multiprocessing.cpu_count() - 1
            if n < 2:
                n = 1
            self.pTransformer = []
            for i in range (n):
                t = VdTransformer(self.warteschlange, i, folder, self.admin)
                t.start()
                self.pTransformer.append(t)
    
    def aufzeichnungStarten (self):
        self.noBreak.value = True
        print("Aufzeichnung wird gestartet...")
        self.scannerStatus.value = "Aufnahme gestartet"
    
    def aufzeichnungStoppen (self):
        self.noBreak.value = False
        print("Aufzeichnung wird innerhalb von 5 Sekunden gestoppt")
        os.wait(5)
        self.pBuffer.terminate()
        self.scannerStatus.value = "Aufnahme gestoppt"
    def herunterFahren(self):
        self.aufzeichnungStoppen();
        os.system("sudo shutdown -h now")
        print ("Faehrt herunter")
        
# Websteuerung
app = Flask(__name__)


@app.route("/")
def webIndex():
    timediff = datetime.now()-ms.date
    laufzeit = str(timediff.seconds + (int(timediff.microseconds/1000)/1000.))
    return """<html>
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
                <td>"""+laufzeit+"""</td></tr>
            <tr><td colspan="2">
                <a href="/starten">Aufzeichnung starten</a></td></tr>
            <tr><td colspan="2">
                <a href="/stoppen">Aufzeichnung stoppen</a></td></tr>
            <tr><td colspan="2">
                <a href="/shutdown">Raspberry herunterfahren</a></td></tr>
            </tr>
        </table>
    </body>
    </html>"""
        
@app.route("/shutdown")
def webShutdown():
    ms.herunterFahren()
    return "Wird in 10 Sekunden heruntergefahren..."

@app.route("/stoppen")
def webStoppen():
    ms.aufzeichnungStoppen()
    return "Aufzeichnung wird gestoppt..."

@app.route("/starten")
def webStarten():
    ms.noBreak.value = True
    print("Aufzeichnung wird gestartet")
    ms.scannerStatus.value = "Aufnahme gestartet"
    return "Aufzeichnung wird gestartet..."

def startWeb():
    print("Webserver startet...")
    app.run('0.0.0.0', 8080)
    
if __name__ == '__main__':
    ms = VdAutoStart()
    t = Thread(target=startWeb)
    t.start()
    ms.run()
    
    
    
