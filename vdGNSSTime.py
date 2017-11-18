#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.18
"""

import datetime
from threading import Thread
import socket
import os
import serial

from vdInterface import VdInterface


class VdGNSSTime(Thread):

    """
    system time by gnss data
    """

    def __init__(self, master):
        """
        Constructor
        :param master: instance of VdAutostart
        :type master: VdAutoStart
        """
        Thread.__init__(self)
        self.tScanner = None
        self.tSerial = None
        self._master = master
        self._conf = master.get_conf()
        self._time_corrected = False

    def run(self):
        """
        starts threads for time detection
        """
        # Thread zur Erkennung der seriellen Schnittstelle
        self.tSerial = Thread(target=self._get_gnss_time_from_serial())
        self.tSerial.start()

        # Thread zur Erkennung des Scanners
        self.tScanner = Thread(target=self._get_gnss_time_from_scanner())
        self.tScanner.start()

        self._master.set_gnss_status("Connecting...")

    def _get_gnss_time_from_scanner(self):
        """ gets data by scanner network stream """
        sock = VdInterface.get_gnss_stream(self._conf)
        sock.settimeout(1)
        self._master.set_gnss_status("Wait for fix...")
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
        """ get data by serial port """
        ser = None
        try:
            port = self._conf.get("Seriell", "GNSSport")
            ser = serial.Serial(port, 9600, timeout=1)
            self._master.set_gnss_status("Wait for fix...")
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
            print("Could not open serial port!")
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
                self._master.set_gnss_status("Got time!")
                return True
        return False

    def _set_system_time(self, timestamp):
        """
        sets system time
        :param timestamp: current timestamp
        :type timestamp: datetime
        :return:
        :rtype:
        """
        os.system("timedatectl set-ntp 0")
        os.system("timedatectl set-time \"" +
                  timestamp.strftime("%Y-%m-%d %H:%M:%S") + "\"")
        os.system(" timedatectl set-ntp 1")
        self._master.set_gnss_status("System time set")

    def stop(self):
        """ stops all threads """
        self._master.set_gnss_status("Stopped")
        self._time_corrected = True
