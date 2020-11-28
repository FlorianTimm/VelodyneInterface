#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2020.11.28
"""

import sqlite3
from vdFile import VdFile
from vdPoint import VdPoint


class VdSQLiteXYZ(VdFile):

    """ class for writing data to sqlite database """

    def _open(self, filename):
        """
        opens a new db file
        :param filename: name of db file
        :type filename: str
        """
        filename = self._make_filename("db", filename)
        print(filename)
        self.__db = sqlite3.connect(filename)
        self.__cursor = self.__db.cursor()
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS raw_data ("
                              "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                              "time FLOAT,"
                              "x FLOAT,"
                              "y FLOAT,"
                              "z FLOAT)")
        self.__db.commit()

    def write(self):
        """ writes data to database """
        insert = []
        for p in self.writing_queue:
            x, y, z = p.get_xyz()
            insert.append((p.time, x, y, z))

        self.__cursor.executemany("INSERT INTO raw_data ("
                                  "time, x, y, z) "
                                  "VALUES (?, ?, ?, ?)", insert)
        self.__db.commit()
        self.clear_writing_queue()

    def close(self):
        """ close database """
        self.__db.close()
