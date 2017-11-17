#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.17
"""

# Modul zur Steuerung der GPIO-Pins
import datetime
from threading import Thread
import socket
import os

from vdInterface import VdInterface


class VdGNSSTime(Thread):

    """
    classdocs
    """

    def __init__(self, master):
        """
        Constructor
        """
        Thread.__init__(self)
        self.tScanner = None
        self.tSerial = None
        self._master = master
        self._conf = master.get_conf()
        self._time_corrected = False

    def run(self):
        """ Start """

        # Thread zur Erkennung der seriellen Schnittstelle
        self.tSerial = Thread(target=self._get_gnss_time_from_serial())
        self.tSerial.start()

        # Thread zur Erkennung des Scanners
        self.tScanner = Thread(target=self._get_gnss_time_from_scanner())
        self.tScanner.start()

        self._master.set_gnss_status("Verbinde...")

    def _get_gnss_time_from_scanner(self):
        sock = VdInterface.get_gnss_stream(self._conf)
        sock.settimeout(1)
        self._master.set_gnss_status("Warte auf Fix...")
        while not self._time_corrected:
            # Daten empfangen vom Scanner
            # print("Daten kommen...")
            try:
                data = sock.recvfrom(2048)[0]  # buffer size is 2048 bytes
                message = data[206:278].decode('utf-8', 'replace')
                if self._get_gnss_time_from_string(message):
                    break
            except socket.timeout:
                continue
            # else:
            #    print(message)
            if data == 'QUIT':
                break
        sock.close()

    def _get_gnss_time_from_serial(self):
        ser = None
        try:
            import serial
            ser = serial.Serial(
                self._conf.get(
                    "Seriell",
                    "GNSSport"),
                9600,
                timeout=1)
            self._master.set_gnss_status("Warte auf Fix...")
            while not self._time_corrected:
                line = ser.readline()
                message = line.decode('utf-8', 'replace')
                if self._get_gnss_time_from_string(message):
                    break
                    # else:
                    #    print(message)
        except serial.SerialTimeoutException:
            pass
        except serial.serialutil.SerialException:
            print("Port konnte nicht geöffnet werden! Falscher Port?")
        finally:
            if ser is not None:
                ser.close()

    def _get_gnss_time_from_string(self, message):
        if message[0:6] == "$GPRMC":
            p = message.split(",")
            if p[2] == "A":
                print("GNSS-Fix")
                timestamp = datetime.strptime(p[1] + "D" + p[9],
                                              '%H%M%S.00D%d%m%y')
                self._set_system_time(timestamp)
                self._time_corrected = True
                self._master.set_gnss_status("Uhrzeit abgerufen")
                return True
        return False

    def _set_system_time(self, timestamp):
        """
        Uhrzeit des Systems setzen
        """
        os.system("timedatectl set-ntp 0")
        os.system("timedatectl set-time \"" +
                  timestamp.strftime("%Y-%m-%d %H:%M:%S") + "\"")
        os.system(" timedatectl set-ntp 1")
        self._master.set_gnss_status("Uhrzeit gesetzt")

    def stop(self):
        self._master.set_gnss_status("Gestoppt")
        self._time_corrected = True
