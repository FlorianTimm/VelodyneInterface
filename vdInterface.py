#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.02
'''

import socket
import sys
import os
from datetime import datetime
from vdConfig import VdConfig

class VdInterface(object):
    '''
    classdocs
    '''
    
    @staticmethod
    def getDataStream():
        return VdInterface.getStream(VdConfig.UDP_IP, VdConfig.UDP_PORT_DATA)
    
    @staticmethod
    def getGNSSStream():
        return VdInterface.getStream(VdConfig.UDP_IP, VdConfig.UDP_PORT_GNSS)
    
    @staticmethod
    def getStream(ip, port):
                # Create Datagram Socket (UDP)
        try :
            sock = socket.socket(socket.AF_INET,    # Socket Family: IPv4
                                 socket.SOCK_DGRAM) # Socket Type: UDP
            print('Socket erstellt')
        except socket.error as msg :
            print('Socket konnte nicht erstellt werden! Fehler ' + 
                  str(msg[0]) + ': ' + msg[1])
            sys.exit()
    
        # Sockets Options
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        # Erlaubt, dass man sich auf einem Rechner mehrfach mit 
        # einem Port verbinden kann. (optional)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
        # Allows broadcast UDP packets to be sent and received.
    
    
        # Bind socket to local host and port
        try:
            sock.bind((ip, port))
        except socket.error as msg:
            print('Bind failed. Fehler ' + str(msg[0]) + ': ' + msg[1])
            sys.exit()
    
        print('Socket verbunden')
    
        #now keep talking with the client
        print('Listening on: ' + ip + ':' + str(port))
        
        return sock

    @staticmethod
    def getGNSSTime(ms):
        ms.gnssStatus = "Verbinde..."
        sock = VdInterface.getGNSSStream()
        print ("Warte auf GNSS-Fix")
        while True:
            # Daten empfangen vom Scanner
            #print("Daten kommen...")
            data = sock.recvfrom(2048)[0] # buffer size is 2048 bytes
            message = data[206:278].decode('utf-8', 'replace')
            if message[0:6] == "$GPRMC":
                p = message.split(",")
                if p[2]=="A":
                    print("GNSS-Fix")
                    timestamp = datetime.strptime(p[1]+"D"+p[9], 
                                                  '%H%M%S.00D%d%m%y')
                    VdInterface.setSystemZeit(timestamp)
                    break
                else:
                    print("noch kein Fix")
                print
            if data=='QUIT': 
                break
        sock.close()
    
    
    @staticmethod
    def setSystemZeit(timestamp):
        '''
        Uhrzeit des Systems setzen
        '''
        os.system("timedatectl set-ntp 0")
        os.system("timedatectl set-time \"" + 
                  timestamp.strftime("%Y-%m-%d %H:%M:%S") + "\"")
        os.system(" timedatectl set-ntp 1") 

        
        
        
