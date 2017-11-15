#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.15
'''

import socket
import sys
import os

class VdInterface(object):
    '''
    classdocs
    '''
    
    @staticmethod
    def getDataStream(config):
        return VdInterface.getStream(config.get("Netzwerk","UDP_IP"),
                                     config.get("Netzwerk","UDP_PORT_DATA"))
    
    @staticmethod
    def getGNSSStream(config):
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
        
        
