#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.17
"""

import configparser
import multiprocessing
import os
import signal
import sys
import time
from datetime import datetime
from multiprocessing import Queue, Manager
from threading import Thread
from flask import Flask
from vdBuffer import VdBuffer
from vdTransformer import VdTransformer
from vdGNSSTime import VdGNSSTime

# Pruefen, ob es sich um einen Raspberry handelt
try:
    import RPi.GPIO as GPIO

    raspberry = True
except ModuleNotFoundError as mne:
    raspberry = False


class VdAutoStart(object):

    """
    Startskript
    """

    # buffer = None

    def __init__(self, web_interface):
        """
        Constructor
        """
        self._vd_hardware = None
        print("Datenschnittstelle fuer VLP-16\n")

        # Konfigurationsdatei laden
        self._conf = configparser.ConfigParser()
        self._conf.read("config.ini")

        # Variablen für Unterprozesse
        self._pBuffer = None
        self._pTransformer = None

        # Pipes fuer Prozesskommunikation erzeugen
        manager = Manager()
        self._gnss_status = "unbekannt"
        # self._gnssReady = manager.Value('gnssReady',False)
        self._go_on_buffer = manager.Value('_go_on_buffer', False)
        self._go_on_transform = manager.Value('_go_on_transform', False)
        self._scanner_status = manager.Value('_scanner_status', "unbekannt")
        self._datasets = manager.Value('_datasets', 0)
        self._date = manager.Value('_date', None)

        # Warteschlange fuer Transformer
        self._queue = Queue()

        # Variable für Thread
        self._webInterface = web_interface

        # pruefen, ob root-Rechte vorhanden sind
        try:
            os.rename('/etc/foo', '/etc/bar')
            self._admin = True
        except IOError:
            self._admin = False

        self._gnss = None

    def run(self):
        """ Starte das Programm """
        # SIGINT-Signal abfangen
        signal.signal(signal.SIGINT, self._signal_handler)

        if raspberry:
            print ("Raspberry Pi wurde erkannt")
            # Hardwaresteuerung starten
            from vdHardware import VdHardware
            self._vd_hardware = VdHardware(self)
            self._vd_hardware.start()
        else:
            print ("Raspberry Pi wurde nicht erkannt")
            print ("Hardwaresteuerung wurde deaktiviert")

        # Zeit gemaess GNSS einstellen
        if self._conf.get("Funktionen", "GNSSZeitVerwenden"):
            self._gnss = VdGNSSTime(self)
            self._gnss.start()

    def start_transformer(self):
        print("Transformer starten...")
        # Transformerprozess gemaess Prozessoranzahl
        if self._conf.get("Funktionen", "activateTransformer"):
            self._go_on_transform.value = True
            n = multiprocessing.cpu_count() - 1
            if n < 2:
                n = 1
            self._pTransformer = []
            for i in range(n):
                t = VdTransformer(i, self)
                t.start()
                self._pTransformer.append(t)

            print(str(n) + " Transformer erzeugt!")

    def start_recording(self):
        if not (self._go_on_buffer.value and self._pBuffer.is_alive()):
            self._go_on_buffer.value = True
            print("Aufzeichnung wird gestartet...")
            self._scanner_status.value = "Aufnahme gestartet"
            # Speicherprozess starten
            self._pBuffer = VdBuffer(self)
            self._pBuffer.start()
        if self._pTransformer is None:
            self.start_transformer()

    def stop_recording(self):
        print("Aufzeichnung wird gestoppt... (10 Sekunden Timeout)")
        self._go_on_buffer.value = False
        self._date.value = None
        if self._pBuffer is not None:
            self._pBuffer.join(10)
            if self._pBuffer.is_alive():
                print ("Beenden war nicht erfolgreich, Prozess wird gekillt!")
                self._pBuffer.terminate()
            print("Aufzeichnung wurde gestoppt!")
        else:
            print ("Aufzeichnung war nie gestartet!")

    def stop_transformer(self):
        print("Umformung wird beendet... (15 Sekunden Timeout)")
        self._go_on_transform.value = False
        if self._pTransformer is not None:
            for pT in self._pTransformer:
                pT.join(15)
                if pT.is_alive():
                    print (
                        "Beenden war nicht erfolgreich, Prozess wird gekillt!")
                    pT.terminate()
            print("Umformung wurde beendet!")
        else:
            print ("Umformung war nie gestartet!")

    @staticmethod
    def stop_web_interface():
        # Todo
        # self._webInterface.exit()
        print ("WebInterface gestoppt!")

    def stop_hardware_control(self):
        if self._vd_hardware is not None:
            self._vd_hardware.stop()
            self._vd_hardware.join(5)

    def stop_childs(self):
        print ("Stoppe Skript...")
        self.stop_recording()
        self.stop_transformer()
        # self.webInterfaceStoppen()
        self.stop_hardware_control()
        print ("Unterprozesse gestoppt")

    def end(self):
        self.stop_childs()
        sys.exit()

    def _signal_handler(self, signal, frame):
        print('Ctrl+C gedrückt!')
        self.stop_childs()
        sys.exit()

    def shutdown(self):
        self.stop_childs()
        print ("Faehrt herunter...")
        os.system("sleep 5s; sudo shutdown -h now")
        print ("Faehrt herunter...")
        sys.exit(0)

    def check_queue(self):
        if self._queue.qsize() > 0:
            return True
        return False

    def check_recording(self):
        if self._pBuffer is not None and self._pBuffer.is_alive():
            return True
        return False

    def check_receiving(self):
        x = self._datasets.value
        time.sleep(0.2)
        y = self._datasets.value
        if x - y > 0:
            return True
        return False

    # Getter-Methoden
    def get_conf(self):
        return self._conf

    def get_gnss_status(self):
        return self._gnss_status

    def get_go_on_buffer(self):
        return self._go_on_buffer

    def get_go_on_transform(self):
        return self._go_on_transform

    def get_scanner_status(self):
        return self._scanner_status

    def get_datasets(self):
        return self._datasets

    def get_date(self):
        return self._date

    def get_root(self):
        return self._admin

    def get_queue(self):
        return self._queue

    # Setter-Methoden
    def set_date(self, date):
        self._date = date

    def set_gnss_status(self, gnss_status):
        self._gnss_status = gnss_status


# Websteuerung
app = Flask(__name__)


@app.route("/")
def web_index():
    laufzeit = "(inaktiv)"
    pps = "(inaktiv)"
    if ms.get_date().value is not None:
        timediff = datetime.now() - ms.get_date().value
        td_sec = timediff.seconds + (int(timediff.microseconds / 1000) / 1000.)
        sec = td_sec % 60
        minu = int((td_sec // 60) % 60)
        h = int(td_sec // 3600)

        laufzeit = '{:02d}:{:02d}:{:06.3f}'.format(h, minu, sec)

        pps = '{:.0f}'.format(ms.get_datasets().value / td_sec)

    elif ms.get_go_on_buffer().value:
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
            <tr><td id="spalte1">GNSS-Status:</td><td>""" + ms.get_gnss_status() + """</td></tr>
            <tr><td>Scanner:</td><td>""" + ms.get_scanner_status().value + """</td></tr>
            <tr><td>Datens&auml;tze:</td>
                <td>""" + str(ms.get_datasets().value) + """</td></tr>
            <tr><td>Warteschleife:</td>
                <td>""" + str(ms.get_queue().qsize()) + """</td></tr>
            <tr><td>Aufnahmezeit:</td>
                <td>""" + laufzeit + """</td>
            </tr>
            <tr><td>Punkt/Sekunde:</td>
                <td>""" + pps + """</td>
            </tr>
        </table><br />
                """
    if ms.check_recording():
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
def css_style():
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
def web_shutdown():
    ms.shutdown()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Wird in 10 Sekunden heruntergefahren..."""


@app.route("/beenden")
def web_exit():
    ms.end()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Wird beendet..."""


@app.route("/stoppen")
def web_stop():
    ms.stop_recording()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Aufzeichnung wird gestoppt..."""


@app.route("/starten")
def web_start():
    ms.start_recording()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Aufzeichnung wird gestartet..."""


def start_web():
    print("Webserver startet...")
    app.run('0.0.0.0', 8080)


if __name__ == '__main__':
    w = Thread(target=start_web)
    ms = VdAutoStart(w)
    w.start()
    ms.run()
