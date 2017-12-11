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

from vdTxtFile import VdTxtFile
from vdXYZFile import VdXYZFile
from vdSQLite import VdSQLite
from vdObjFile import VdObjFile


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

        print("Transformer started!")
        while self.__go_on_transform.value:
            try:
                # get file name from queue
                filename = self.__queue.get(True, 2)
                folder = os.path.dirname(filename)
                trans = self.__conf.get("file", "transformer")
                fileformat = self.__conf.get("file", "format")
                new_file = ""
                if fileformat == "txt":
                    new_file = folder + "/txt_file" + str(self.__number)
                elif fileformat == "obj":
                    new_file = folder + "/obj_file" + str(self.__number)
                elif fileformat == "xyz":
                    new_file = folder + "/xyz_file" + str(self.__number)
                elif fileformat == "sql":
                    new_file = folder + "/sqlite"

                if trans == "python":
                    if folder != old_folder:
                        if fileformat == "txt":
                            vd_file = VdTxtFile(
                                self.__conf, new_file)
                        elif fileformat == "obj":
                            vd_file = VdObjFile(
                                self.__conf, new_file)
                        elif fileformat == "xyz":
                            vd_file = VdXYZFile(
                                self.__conf, new_file)
                        elif fileformat == "sql":
                            vd_file = VdSQLite(
                                self.__conf, new_file)
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
                else:
                    result = subprocess.run(['./' + trans, "bin", filename, fileformat, new_file],
                                            stdout=subprocess.PIPE)
                    print(result.stdout.decode('utf-8'))

                # delete binary file
                if self.__conf.get("file", "deleteBin") == "True":
                    os.remove(f.name)
                else:
                    dir = os.path.dirname(folder)
                    fname = os.path.basename(filename)
                    os.rename(filename, dir + "/transformed/" + fname)
            except Empty:
                print("Queue empty!")
                continue
