#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.12.12
"""

import os
import signal
import socket
from datetime import datetime
from multiprocessing import Process

from vdInterface import VdInterface


class VdBuffer(Process):

    """ process for buffering binary data """

    def __init__(self, master):
        """
        Constructor
        :param master: instance of VdAutoStart
        :type master: VdAutoStart
        """
        # constructor of super class
        Process.__init__(self)

        # safe pipes
        # self.__master = master
        self.__go_on_buffering = master.go_on_buffer
        self.__scanner_status = master.scanner_status
        self.__datasets = master.dataset_cnt
        self.__queue = master.queue
        self.__admin = master.admin
        self.__date = master.date
        self.__conf = master.conf

        self.__file_no = 0

    @staticmethod
    def __signal_handler(sig_no, frame):
        """
        handles SIGINT-signal
        :param sig_no: signal number
        :type sig_no: int
        :param frame:execution frame
        :type frame: frame
        """
        del sig_no, frame
        # self.master.end()
        print("SIGINT vdBuffer")

    def __new_folder(self):
        """ creates data folder """
        # checks time for file name and runtime
        self.__date.value = datetime.now()
        dir = self.__conf.get("file", "namePre")
        dir += self.__date.value.strftime(
            self.__conf.get("file", "timeFormat"))
        self.__folder = dir + "/_buffer"
        # make folder
        os.makedirs(self.__folder)
        os.makedirs(dir + "/_transformed")
        print("Data folder: " + self.__folder)

    def run(self):
        """ starts buffering process """
        signal.signal(signal.SIGINT, self.__signal_handler)

        # open socket to scanner
        sock = VdInterface.get_data_stream(self.__conf)
        self.__scanner_status.value = "Socket connected"

        buffer = b''
        datasets_in_buffer = 0

        self.__datasets.value = 0

        # process priority
        if self.__admin:
            os.nice(-18)

        transformer = self.__conf.get(
            "functions",
            "activateTransformer") == "True"
        measurements_per_dataset = int(self.__conf.get(
            "device", "valuesPerDataset"))
        bufferTakt = int(self.__conf.get(
            "file", "takt"))

        sock.settimeout(1)
        while self.__go_on_buffering.value:
            try:
                # get data from scanner
                data = sock.recvfrom(1248)[0]

                if datasets_in_buffer == 0 and self.__file_no == 0:
                    self.__new_folder()
                # RAM-buffer
                buffer += data
                datasets_in_buffer += 1
                self.__datasets.value += measurements_per_dataset
                # safe data to file every 1500 datasets
                # (about 5 or 10 seconds)
                if (datasets_in_buffer >= bufferTakt) or \
                        (not self.__go_on_buffering.value):
                    # write file
                    f = open(
                        self.__folder + "/" + str(self.__file_no) + ".bin",
                        "wb")
                    f.write(buffer)

                    f.close()

                    if transformer:
                        self.__queue.put(f.name)

                    # clear buffer
                    buffer = b''
                    datasets_in_buffer = 0

                    # count files
                    self.__file_no += 1

                if data == 'QUIT':
                    break
            except socket.timeout:
                print("No data")
                continue
        sock.close()
        self.__scanner_status.value = "recording stopped"
        print("Disconnected!")
