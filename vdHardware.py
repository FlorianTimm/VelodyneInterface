#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.10.27
'''

# Modul zur Steuerung der GPIO-Pins
import RPi.GPIO as GPIO
import time
from threading import Thread

class VdHardware(Thread):
    '''
    classdocs
    '''

    def __init__(self, masterSkript):
        '''
        Constructor
        '''
        Thread.__init__(self)
        
        GPIO.setmode(GPIO.BOARD)

        # EIngaenge aktivieren
        GPIO.setup(18, GPIO.IN) # Aufzeichnung stoppen
        GPIO.setup(16, GPIO.IN) # Herunterfahren
        
        # Ausgaenge aktivieren
        GPIO.setup(13, GPIO.OUT) # GPS-Fix
        GPIO.setup(15, GPIO.OUT) # Laserscanner (blink)
        
        # Ausgaenge auf Low schalten
        GPIO.output(13, GPIO.LOW)
        GPIO.output(15, GPIO.LOW)
        
        # Masterobjekt sichern
        self.masterSkript = masterSkript
        
    def run(self):
        # Counter fuer gedrueckt halten initialisieren
        herunterfahren = 0
        stoppen = 0
        
        #prüfen, ob Modul angeschlossen ist
        if GPIO.input(16) != GPIO.LOW or GPIO.input(18) != GPIO.LOW:
            print("Hardwaremodul nicht erkannt")
            self.exit()
        
        # Dauerschleife zur Input/Output-Steuerung
        while True:
            # "Aufzeichnung stoppen" gedrueckt
            if GPIO.input(18) == GPIO.HIGH:
                stoppen += 1
                
            # "Herunterfahren" gedrueckt
            if GPIO.input(16) == GPIO.HIGH:
                herunterfahren += 1
            
            # Stoppen laenger als 2 Sekunden gedrueckt
            if stoppen > 10:
                self.masterSkript.aufzeichnungStoppen()
                stoppen = 0
                
            # Herunterfahren laenger als 2 Sekunden gedrueckt
            if herunterfahren > 10:
                self.masterSkript.herunterFahren()
                herunterfahren = 0
            
            # Pause zur Festlegung der Abtastrate
            time.sleep(0.2)
        
    
        
        
