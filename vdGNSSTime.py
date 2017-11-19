#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.19
"""

from datetime import datetime
from threading import Thread
import socket
import os
import serial

from vdInterface import VdInterface


class VdGNSSTime(Thread):

    """ system time by gnss data """

    def __init__(self, master):
        """
        Constructor
        :param master: instance of VdAutoStart
        :type master: VdAutoStart
        """
        Thread.__init__(self)
        self.__tScanner = None
        self.__tSerial = None
        self.__master = master
        self.__conf = master.conf
        self.__time_corrected = False

    def run(self):
        """
        starts threads for time detection
        """
        # get data from serial port
        self.__tSerial = Thread(target=self.__get_gnss_time_from_serial())
        self.__tSerial.start()

        # get data from scanner
        self.__tScanner = Thread(target=self.__get_gnss_time_from_scanner())
        self.__tScanner.start()

        self.__master.gnss_status = "Connecting..."

    def __get_gnss_time_from_scanner(self):
        """ gets data by scanner network stream """
        sock = VdInterface.get_gnss_stream(self.__conf)
        sock.settimeout(1)
        self.__master.gnss_status = "Wait for fix..."
        while not self.__time_corrected:
            try:
                data = sock.recvfrom(2048)[0]  # buffer size is 2048 bytes
                message = data[206:278].decode('utf-8', 'replace')
                if self.__get_gnss_time_from_string(message):
                    break
            except socket.timeout:
                continue
            # else:
            #    print(message)
            if data == 'QUIT':
                break
        sock.close()

    # noinspection PyArgumentList
    def __get_gnss_time_from_serial(self):
        """ get data by serial port """
        ser = None
        try:
            port = self.__conf.get("serial", "GNSSport")
            ser = serial.Serial(port, timeout=1)
            self.__master.gnss_status = "Wait for fix..."
            while not self.__time_corrected:
                line = ser.readline()
                message = line.decode('utf-8', 'replace')
                if self.__get_gnss_time_from_string(message):
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

    def __get_gnss_time_from_string(self, message):
        if message[0:6] == "$GPRMC":
            p = message.split(",")
            if p[2] == "A":
                print("GNSS-Fix")
                timestamp = datetime.strptime(p[1] + "D" + p[9],
                                              '%H%M%S.00D%d%m%y')
                self.__set_system_time(timestamp)
                self.__time_corrected = True
                self.__master.gnss_status = "Got time!"
                return True
        return False

    def __set_system_time(self, timestamp):
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
        self.__master.set_gnss_status("System time set")

    def stop(self):
        """ stops all threads """
        self.__master.gnss_status = "Stopped"
        self.__time_corrected = True
