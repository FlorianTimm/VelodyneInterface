#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.16
'''

from vdBuffer import VdBuffer
from vdInterface import VdInterface
from vdTransformer import VdTransformer
from vdGNSStime import VdGNSStime
import time

from datetime import datetime
from multiprocessing import Queue, Manager
import multiprocessing
from threading import Thread
from flask import Flask
import os
import sys
import signal
import configparser

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
    # buffer = None

    def __init__(self, webInterface):
        '''
        Constructor
        '''
        print("Datenschnittstelle fuer VLP-16\n")

        # Konfigurationsdatei laden
        self.conf = configparser.ConfigParser()
        self.conf.read("config.ini")

        # Variablen für Unterprozesse
        self.pBuffer = None
        self.pTransformer = None

        # Pipes fuer Prozesskommunikation erzeugen
        manager = Manager()
        self.gnssStatus = "unbekannt"
        # self.gnssReady = manager.Value('gnssReady',False)
        self.noBreak = manager.Value('noBreak', False)
        self.weiterUmformen = manager.Value('weiterUmformen', False)
        self.scannerStatus = manager.Value('scannerStatus', "unbekannt")
        self.datensaetze = manager.Value('datensaetze', 0)
        self.date = manager.Value('date', None)

        # Warteschlange fuer Transformer
        self.warteschlange = Queue()

        # Variable für Thread
        self.webInterface = webInterface

        # Auf Signale reagieren
        signal.signal(signal.SIGINT, self.signal_handler)

        # pruefen, ob root-Rechte vorhanden sind
        try:
            os.rename('/etc/foo', '/etc/bar')
            self.admin = True
        except IOError as e:
            self.admin = False

    def signal_handler(self, signal, frame):
        self.ende()

    def run(self):
        ''' Starte das Programm '''
        # SIGINT-Signal abfangen
        signal.signal(signal.SIGINT, self.signal_handler)

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
        if self.conf.get("Funktionen", "GNSSZeitVerwenden"):
            from vdGNSStime import VdGNSStime
            self.gnss = VdGNSStime(self)
            self.gnss.start()

    def transformerStarten(self):
        print("Transformer starten...")
        # Transformerprozess gemaess Prozessoranzahl
        if self.conf.get("Funktionen", "activateTransformer"):
            self.weiterUmformen.value = True
            n = multiprocessing.cpu_count() - 1
            if n < 2:
                n = 1
            self.pTransformer = []
            for i in range(n):
                t = VdTransformer(i, self)
                t.start()
                self.pTransformer.append(t)

            print(str(n) + " Transformer erzeugt!")

    def aufzeichnungStarten(self):
        if not(self.noBreak.value and self.pBuffer.is_alive()):
            self.noBreak.value = True
            print("Aufzeichnung wird gestartet...")
            self.scannerStatus.value = "Aufnahme gestartet"
            # Speicherprozess starten
            self.pBuffer = VdBuffer(self)
            self.pBuffer.start()
        if self.pTransformer is None:
            self.transformerStarten()

    def aufzeichnungStoppen(self):
        print("Aufzeichnung wird gestoppt... (10 Sekunden Timeout)")
        self.noBreak.value = False
        self.date.value = None
        if self.pBuffer is not None:
            self.pBuffer.join(10)
            if (self.pBuffer.is_alive()):
                print ("Beenden war nicht erfolgreich, Prozess wird gekillt!")
                self.pBuffer.terminate()
            print("Aufzeichnung wurde gestoppt!")
        else:
            print ("Aufzeichnung war nie gestartet!")

    def transformerStoppen(self):
        print("Umformung wird beendet... (15 Sekunden Timeout)")
        self.weiterUmformen.value = False
        if self.pTransformer is not None:
            for pT in self.pTransformer:
                pT.join(15)
                if pT.is_alive():
                    print (
                        "Beenden war nicht erfolgreich, Prozess wird gekillt!")
                    pT.terminate()
            print("Umformung wurde beendet!")
        else:
            print ("Umformung war nie gestartet!")

    def webInterfaceStoppen(self):
        # Todo
        # self.webInterface.exit()
        print ("WebInterface gestoppt!")

    def hardwareSteuerungStoppen(self):
        if self.vdH is not None:
            self.vdH.stoppe()
            self.vdH.join(5)

    def stoppeKinder(self):
        print ("Stoppe Skript...")
        self.aufzeichnungStoppen()
        self.transformerStoppen()
        # self.webInterfaceStoppen()
        self.hardwareSteuerungStoppen()
        print ("Unterprozesse gestoppt")

    def ende(self):
        self.stoppeKinder()
        sys.exit()

    def signal_handler(self, signal, frame):
        print('Ctrl+C gedrückt!')
        self.stoppeKinder()
        sys.exit()

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
    laufzeit = "(inaktiv)"
    pps = "(inaktiv)"
    if ms.date.value is not None:
        timediff = datetime.now() - ms.date.value
        td_sec = timediff.seconds + (int(timediff.microseconds / 1000) / 1000.)
        sec = td_sec % 60
        min = int((td_sec // 60) % 60)
        h = int(td_sec // 3600)

        laufzeit = '{:02d}:{:02d}:{:06.3f}'.format(h, min, sec)
        
        pps = '{:.0f}'.format(ms.datensaetze.value/td_sec)
        
    elif ms.noBreak.value:
        laufzeit = "(noch keine Daten)"

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
            <tr><td id="spalte1">GNSS-Status:</td><td>""" + ms.gnssStatus + """</td></tr>
            <tr><td>Scanner:</td><td>""" + ms.scannerStatus.value + """</td></tr>
            <tr><td>Datens&auml;tze:</td>
                <td>""" + str(ms.datensaetze.value) + """</td></tr>
            <tr><td>Warteschleife:</td>
                <td>""" + str(ms.warteschlange.qsize()) + """</td></tr>
            <tr><td>Aufnahmezeit:</td>
                <td>""" + laufzeit + """</td>
            </tr>
            <tr><td>Punkt/Sekunde:</td>
                <td>""" + pps + """</td>
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
    ms.ende()
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
