/*!
 *  \brief		class for writing data to sqlite database
 *
 *  \author		Florian Timm
 *  \version	2020.11.28
 *  \copyright	MIT License
 */

#include "VdSQLiteXYZ.h"
#include <stdio.h>
#include <iostream>
#include <sqlite3.h>
using namespace std;

VdSQLiteXYZ::VdSQLiteXYZ(string filename) {
	/**
	 * constructor
	 * @param filename name of db file
	 */
	this->open(filename);
	sqlite3 *db;
}

void VdSQLiteXYZ::open(string filename) {
	/**
	 * opens a new db file
	 * @param filename name of db file
	 */
	char *zErrMsg = 0;
	filename = this->makeFilename(string("db"), filename);
	sqlite3_open(filename.c_str(), &this->db);

	string sql =
			"CREATE TABLE IF NOT EXISTS xyz_data (id INTEGER PRIMARY KEY AUTOINCREMENT, time FLOAT, x FLOAT, y FLOAT, z FLOAT)";
	sqlite3_exec(this->db, sql.c_str(), 0, 0, &zErrMsg);
	sqlite3_prepare_v2(db,
			"INSERT INTO xyz_data (time, x, y, z) VALUES (?, ?, ?, ?)",
			-1, &stmt, 0);
}

void VdSQLiteXYZ::write() {
	/** writes data to database */
	char *zErrMsg = 0;
	sqlite3_exec(this->db, "BEGIN TRANSACTION;", 0, 0, &zErrMsg);
	for (VdPoint p : this->writingQueue) {
		sqlite3_bind_double(stmt, 1, p.getTime());
		VdXYZ xyz = p.getXYZ();
		sqlite3_bind_double(stmt, 2, xyz.getX());
		sqlite3_bind_double(stmt, 3, xyz.getY());
		sqlite3_bind_double(stmt, 4, xyz.getZ());
		sqlite3_step(stmt);
		sqlite3_reset(stmt);
	}
	sqlite3_exec(this->db, "END TRANSACTION;", 0, 0, &zErrMsg);
	this->clearWritingQueue();
}
void VdSQLiteXYZ::close() {
	/** close database */
	sqlite3_close(db);
}
