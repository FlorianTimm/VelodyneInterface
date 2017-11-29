/*
 * VdSQLite.cpp
 *
 *  Created on: 29.11.2017
 *      Author: timm
 */

#include "VdSQLite.h"
#include <stdio.h>
#include <iostream>
#include <sqlite3.h>
using namespace std;

VdSQLite::VdSQLite(string filename) {
	// class for writing data to sqlite database
	this->open(filename);
	sqlite3 *db;
}

void VdSQLite::open(string filename) {
	/*
	 opens a new db file
	 :param filename: name of db file
	 :type filename: str
	 */
	char *zErrMsg = 0;
	filename = this->makeFilename(string("db"), filename);
	sqlite3_open(filename.c_str(), &this->db);

	string sql =
			"CREATE TABLE IF NOT EXISTS raw_data (id INTEGER PRIMARY KEY AUTOINCREMENT, time FLOAT, azimuth FLOAT, vertical FLOAT, distance FLOAT, reflection INTEGER)";
	sqlite3_exec(this->db, sql.c_str(), 0, 0, &zErrMsg);
	sqlite3_prepare_v2(db,
			"INSERT INTO raw_data (time, azimuth, vertical, distance, reflection) VALUES (?, ?, ?, ?, ?)",
			-1, &stmt, 0);
}

void VdSQLite::write() {
	// writes data to database
	char *zErrMsg = 0;
	sqlite3_exec(this->db, "BEGIN TRANSACTION;", 0, 0, &zErrMsg);
	for (VdPoint p : this->writingQueue) {
		sqlite3_bind_double(stmt, 1, p.getTime());
		sqlite3_bind_double(stmt, 2, p.getAzimuth());
		sqlite3_bind_double(stmt, 3, p.getVertical());
		sqlite3_bind_double(stmt, 4, p.getDistance());
		sqlite3_bind_int(stmt, 5, p.getReflection());
		sqlite3_step(stmt);
		sqlite3_reset(stmt);
	}
	sqlite3_exec(this->db, "END TRANSACTION;", 0, 0, &zErrMsg);
	this->clearWritingQueue();
}
void VdSQLite::close() {
	// close database
	sqlite3_close(db);
}

