#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.27
"""

import sqlite3
from vdFile import VdFile
from vdPoint import VdPoint


class VdSQLite(VdFile):
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
                              "azimuth FLOAT,"
                              "vertical FLOAT,"
                              "distance FLOAT,"
                              "reflection INTEGER)")
        self.__db.commit()

    def write(self):
        """ writes data to database """
        insert = []
        for p in self.writing_queue:
            insert.append((p.time, p.azimuth, p.vertical,
                           p.distance, p.reflection))

        self.__cursor.executemany("INSERT INTO raw_data ("
                                  "time, azimuth, vertical, "
                                  "distance, reflection) "
                                  "VALUES (?, ?, ?, ?, ?)", insert)
        self.__db.commit()
        self.clear_writing_queue()

    def close(self):
        """ close database """
        self.__db.close()
