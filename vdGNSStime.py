#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.12
'''

# Modul zur Steuerung der GPIO-Pins
import time
from threading import Thread
from vdConfig import VdConfig
from vdInterface import VdInterface

class VdGNSStime(Thread):
    '''
    classdocs
    '''

    def __init__(self, masterSkript):
        '''
        Constructor
        '''
        Thread.__init__(self)
        self.masterSkript = masterSkript
        
        self.zeitGefunden = False
        
        
    def run(self):       
        """ Start """
        # Thread zur Erkennung der seriellen Schnittstelle
        self.s = Thread(target=self.getGNSSTimeFromSerial())
        self.s.start()
        
        # Thread zur Erkennung des Scanners
        self.l = Thread(target=self.getGNSSTimeFromScanner())
        self.l.start()
        
        self.masterSkript.gnssStatus = "Verbinde..."
        
    def getGNSSTimeFromScanner(self):
        self.masterSkript.gnssStatus = "Verbinde..."
        sock = VdInterface.getGNSSStream()
        sock.settimeout(1)
        self.masterSkript.gnssStatus = "Warte auf Fix..."
        while not self.zeitGefunden:
            # Daten empfangen vom Scanner
            #print("Daten kommen...")
            try:
                data = sock.recvfrom(2048)[0] # buffer size is 2048 bytes
                message = data[206:278].decode('utf-8', 'replace')
                if self.getGNSSTimeFromString(message):
                    break
            except Exception:
                continue
            #else:
            #    print(message)
            if data=='QUIT': 
                break
        sock.close()
    
    
    def getGNSSTimeFromSerial(self):
        ser = None
        try:
            import serial
            ser = serial.Serial(VdConfig.GNSSport, 9600, timeout=1)
            self.masterSkript.gnssStatus = "Warte auf Fix..."
            while not self.zeitGefunden:
                line = ser.readline()
                message = line.decode('utf-8', 'replace')
                if self.getGNSSTimeFromString(message):
                    break;
                #else:
                #    print(message)
        except Exception:
            print()
        finally:
            if ser != None:
                ser.close()
        
        
    def getGNSSTimeFromString(self, message):
        if message[0:6] == "$GPRMC":
            p = message.split(",")
            if p[2]=="A":
                print("GNSS-Fix")
                timestamp = datetime.strptime(p[1]+"D"+p[9], 
                                                  '%H%M%S.00D%d%m%y')
                VdInterface.setSystemZeit(timestamp)
                self.zeitGefunden = True
                return True
        return False
            
    
    def setSystemZeit(self,timestamp):
        '''
        Uhrzeit des Systems setzen
        '''
        os.system("timedatectl set-ntp 0")
        os.system("timedatectl set-time \"" + 
                  timestamp.strftime("%Y-%m-%d %H:%M:%S") + "\"")
        os.system(" timedatectl set-ntp 1") 

    def stoppe(self):
        self.zeitGefunden = True
