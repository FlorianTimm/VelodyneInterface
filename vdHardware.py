#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.12
'''

# Modul zur Steuerung der GPIO-Pins
import RPi.GPIO as GPIO
import time
import multiprocessing
from threading import Thread
import threading


class VdHardware(Thread):

    '''
    classdocs
    '''

    def __init__(self, masterSkript):
        '''
        Constructor
        '''
        Thread.__init__(self)

        GPIO.setmode(GPIO.BCM)

        self.taster1 = 18  # Start / Stop
        self.taster2 = 25  # Herunterfahren

        # LED-Pins:
        # 0: Datenempfang
        # 1: Warteschleife
        # 2: Aufzeichnung
        self.led = [10, 9, 11]
        self.datenempfang = False
        self.warteschlange = False
        self.aufzeichung = False

        # Masterobjekt sichern
        self.masterSkript = masterSkript

        # Eingaenge aktivieren
        # Aufzeichnung starten/stoppen
        GPIO.setup(self.taster1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Herunterfahren
        GPIO.setup(self.taster2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Ausgaenge aktivieren und auf Low schalten
        for l in self.led:
            GPIO.setup(l, GPIO.OUT)  # GPS-Fix
            GPIO.output(l, GPIO.LOW)

        self.weiter = True

    def run(self):
        '''
        Ausfuehrung des Prozesses
        '''
        GPIO.add_event_detect(self.taster1, GPIO.FALLING, self.taster1Pressed)
        GPIO.add_event_detect(self.taster2, GPIO.FALLING, self.taster1Pressed)

        self.timerCheckLEDs()

    def timerCheckLEDs(self):
        self.checkLEDs()
        if self.weiter:
            t = threading.Timer(1, self.timerCheckLEDs)
            t.start()

    def checkLEDs(self):
        self.pruefeAufzeichung()
        self.pruefeDatenempfang()
        self.pruefeWarteschlange()

    def taster1Pressed(self):
        time.sleep(0.1)  # Prellen abwarten

        # mindestens 2 Sekunden druecken
        warten = GPIO.wait_for_edge(self.taster1, GPIO.RISING, timeout=1900)

        if warten is None:
            # keine steigende Kante = gehalten
            if self.masterSkript.noBreak.value:
                self.masterSkript.aufzeichnungStoppen()
            else:
                self.masterSkript.aufzeichnungStarten()

    def taster2Pressed(self):
        time.sleep(0.1)  # Prellen abwarten

        # mindestens 2 Sekunden druecken
        warten = GPIO.wait_for_edge(self.taster2, GPIO.RISING, timeout=1900)

        if warten is None:
            # keine steigende Kante = gehalten
            self.masterSkript.herunterFahren()

    def schalteLED(self, led, janein):
        if janein:
            GPIO.output(self.led[led], GPIO.HIGH)
        else:
            GPIO.output(self.led[led], GPIO.LOW)

    def aktualisiereLEDs(self):
        self.schalteLED(0, self.datenempfang)
        self.schalteLED(1, self.warteschlange)
        self.schalteLED(2, self.aufzeichung)

    def setDatenempfang(self, janein):
        if self.datenempfang != janein:
            self.datenempfang = janein
            self.aktualisiereLEDs()

    def setWarteschlange(self, janein):
        if self.warteschlange != janein:
            self.warteschlange = janein
            self.aktualisiereLEDs()

    def setAufzeichung(self, janein):
        if self.aufzeichung != janein:
            self.aufzeichung = janein
            self.aktualisiereLEDs()

    def pruefeWarteschlange(self):
        if self.masterSkript.warteschlange.qsize() > 0:
            self.setWarteschlange(True)
        else:
            self.setWarteschlange(True)

    def pruefeAufzeichung(self):
        if self.masterSkript.pBuffer is not None and self.masterSkript.pBuffer.is_alive():
            self.setAufzeichung(True)
        else:
            self.setAufzeichung(True)

    def pruefeDatenempfang(self):
        x = self.masterSkript.datensaetze.value
        time.sleep(0.2)
        y = self.masterSkript.datensaetze.value
        if x - y > 0:
            self.setDatenempfang(True)
        else:
            self.setDatenempfang(False)

    def stoppe(self):
        self.weiter = False
        GPIO.cleanup()
