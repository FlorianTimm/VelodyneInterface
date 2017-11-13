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
import sys

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

    def __init__(self, webInterface):
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
        self.weiterUmformen = manager.Value('weiterUmformen', False)
        self.scannerStatus = manager.Value('scannerStatus', "unbekannt")
        self.datensaetze = manager.Value('datensaetze', 0)
        self.date = manager.Value('date', datetime.now())
        
        self.pBuffer = None
        self.pTransformer = []
        
        self.webInterface = webInterface

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
            self.vdH = VdHardware(self)
            self.vdH.start()
        else:
            self.vdH = None
            print ("Raspberry Pi wurde nicht erkannt")
            print ("Hardwaresteuerung wurde deaktiviert")
            
            
        # Zeit gemaess GNSS einstellen
        if VdConfig.aufGNSSwarten:
            print ("Warte auf GNSS-Signal...")
            VdInterface.getGNSSTime(ms)
        

         
        # Transformerprozess gemaess Prozessoranzahl
        if VdConfig.activateTransformer:
            self.weiterUmformen.value = True
            n = multiprocessing.cpu_count() - 1
            if n < 2:
                n = 1
            self.pTransformer = []
            for i in range (n):
                t = VdTransformer(self.warteschlange, i, self.admin, self.weiterUmformen)
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
        print("Aufzeichnung wird gestoppt... (10 Sekunden Timeout)")
        self.noBreak.value = False
        if self.pBuffer != None:
            self.pBuffer.join(10)
            if (self.pBuffer.is_alive()):
                print ("Beenden war nicht erfolgreich, Prozess wird gekillt!")
                self.pBuffer.terminate()
            print("Aufzeichnung wurde gestoppt!")
        else:
            print ("Aufzeichnung war nie gestartet!")
        
            
            
    def transformerStoppen (self):
        print("Umformung wird beendet... (15 Sekunden Timeout)")
        self.weiterUmformen.value = False
        for t in self.pTransformer:
            t.join(15)
            if t.is_alive():
                print ("Beenden war nicht erfolgreich, Prozess wird gekillt!")
                t.terminate()
        print("Umformung wurde beendet!")
        
    def webInterfaceStoppen (self):
        #Todo
        #self.webInterface.exit()
        print ("WebInterface gestoppt!")
        
    def hardwareSteuerungStoppen(self):
        if self.vdH != None:
            self.vdH.stoppe()
            self.vdH.join(5)
            
    def stoppeKinder(self):
        print ("Stoppe Skript...")
        self.aufzeichnungStoppen();
        self.transformerStoppen()
        #self.webInterfaceStoppen()
        self.hardwareSteuerungStoppen()
        print ("Unterprozesse gestoppt")
            
            
    def exit(self):
        self.stoppeKinder()
        sys.exit(0)
        
    def herunterFahren(self):
        self.stoppeKinder()
        print ("Faehrt herunter...")
        os.system("sleep 5s; sudo shutdown -h now")
        print ("Faehrt herunter...")
        sys.exit(0)
# Websteuerung
app = Flask(__name__)


@app.route("/")
def webIndex():
    timediff = datetime.now()-ms.date.value
    laufzeit = str(timediff.seconds + (int(timediff.microseconds/1000)/1000.))
    ausgabe = """<html>
    <head>
        <title>VLP16-Datenschnittstelle</title>
        <meta name="viewport" content="width=device-width; initial-scale=1.0;" /> 
        <link href="/style.css" rel="stylesheet">
        <meta http-equiv="refresh" content="5; URL=/">
    </head>
    <body>
    <content>
        <h2>VLP16-Datenschnittstelle</h3>
        <table style="">
            <tr><td id="spalte1">GNSS-Status:</td><td>"""+ms.gnssStatus+"""</td></tr>
            <tr><td>Scanner:</td><td>"""+ms.scannerStatus.value+"""</td></tr>
            <tr><td>Datens&auml;tze:</td>
                <td>"""+str(ms.datensaetze.value)+"""</td></tr>
            <tr><td>Warteschleife:</td>
                <td>"""+str(ms.warteschlange.qsize())+"""</td></tr>
            <tr><td>Laufzeit</td>
                <td>"""+laufzeit+"""</td>
            </tr>
        </table><br />
                """
    if ms.noBreak.value and ms.pBuffer.is_alive():
        ausgabe += """<a href="/stoppen" id="stoppen">
            Aufzeichnung stoppen</a><br />"""
    else:
        ausgabe += """<a href="/starten" id="starten">
            Aufzeichnung starten</a><br />"""  
    ausgabe += """
        <a href="/beenden" id="beenden">Skript beenden<br />
        (herunterfahren nur noch über SSH)</a></td></tr><br />
        <a href="/shutdown" id="shutdown">Raspberry herunterfahren</a>
    </content>
    </body>
    </html>"""
    
    return ausgabe
        
@app.route("/style.css")
def cssStyle():
    return """
    body, html, content {
        text-align: center;
    }
    
    content {
        max-width: 15cm;
        display: block;
        margin: auto;
    }
    
    table {
        border-collapse: collapse;
        width: 90%;
        margin: auto;
    }
          
    td {
        border: 1px solid black;
        padding: 1px 2px;
    }
    
    td#spalte1 {
        width: 30%;
    }
            
    a {
        display: block;
        width: 90%;
        padding: 0.5em 0;
        text-align: center;
        margin: auto;
        color: #fff;
    }
    
    a#stoppen {
        background-color: #e90;
    }
            
    a#shutdown {
        background-color: #b00;
    }
            
    a#starten {            
        background-color: #1a1;
    }
            
    a#beenden {
        background-color: #f44;
    }
    """        

@app.route("/shutdown")
def webShutdown():
    ms.herunterFahren()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Wird in 10 Sekunden heruntergefahren..."""
    
@app.route("/beenden")
def webBeenden():
    ms.exit()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Wird beendet..."""
    


@app.route("/stoppen")
def webStoppen():
    ms.aufzeichnungStoppen()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Aufzeichnung wird gestoppt..."""

@app.route("/starten")
def webStarten():
    ms.aufzeichnungStarten()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Aufzeichnung wird gestartet..."""

def startWeb():
    print("Webserver startet...")
    app.run('0.0.0.0', 8080)
    
if __name__ == '__main__':
    w = Thread(target=startWeb)
    ms = VdAutoStart(w)
    w.start()
    ms.run()
    
