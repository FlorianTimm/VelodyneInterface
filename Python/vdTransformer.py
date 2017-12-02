#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.20
"""
import os
import signal
import subprocess
from multiprocessing import Process
from queue import Empty

from vdDataset import VdDataset

from vdFile import VdTxtFile


class VdTransformer(Process):

    """ Process for transforming data from Velodyne VLP-16 """

    def __init__(self, number, master):
        """
        Constructor
        :param number: number of process
        :type number: int
        :param master: instance of VdAutoStart
        :type master: VdAutoStart
        """

        # constructor of super class
        Process.__init__(self)

        self.__queue = master.queue
        self.__number = number
        self.__admin = master.admin
        self.__go_on_transform = master.go_on_transform
        self.__conf = master.conf

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
        print("SIGINT vdTransformer")

    def run(self):
        """ starts transforming process """
        signal.signal(signal.SIGINT, self.__signal_handler)

        if self.__admin:
            os.nice(-15)

        old_folder = ""

        print ("Transformer started!")
        while self.__go_on_transform.value:
            try:
                # get file name from queue
                filename = self.__queue.get(True, 2)
                folder = os.path.dirname(filename)
                trans = self.__conf.get("file", "transformer")
                if trans == "python":
                    if dir != old_folder:
                        vd_file = VdTxtFile(
                            self.__conf,
                            folder + "/obj_file" + str(self.__number))
                        old_folder = folder
    
                    f = open(filename, "rb")
    
                    # count number of datasets
                    file_size = os.path.getsize(f.name)
                    dataset_cnt = int(file_size / 1206)
    
                    for i in range(dataset_cnt):
                        # read next
                        vd_data = VdDataset(self.__conf, f.read(1206))
    
                        # convert data
                        vd_data.convert_data()
    
                        # add them on writing queue
                        vd_file.add_dataset(vd_data.get_data())
    
                        # write file
                        vd_file.write()
                        # close file
                    f.close()
                    break
                elif trans == "linux64":
                    result = subprocess.run(['./vdTrans_Linux_64', "bin", filename, "txt", new_file], stdout=subprocess.PIPE)
                    print(result.stdout.decode('utf-8'))
                elif trans == "arm320":
                    result = subprocess.run(['./vdTrans_arm32', "bin", filename, "txt", new_file], stdout=subprocess.PIPE)
                    print(result.stdout.decode('utf-8'))
                    pass
                
                # delete binary file
                if self.__conf.get("file", "deleteBin") == "True":
                     os.remove(f.name)
            except Empty:
                print("Queue empty!")
                continue
