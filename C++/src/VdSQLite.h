/*
 * VdSQLite.h
 *
 *  Created on: 29.11.2017
 *      Author: timm
 */

#ifndef VDSQLITE_H_
#define VDSQLITE_H_

#include "VdFile.h"
#include <sqlite3.h>
#include <string>
using namespace std;

class VdSQLite : public VdFile{
public:
	VdSQLite(string filename = "");
	void write();
protected:
	void open(std::string filename = "");
	void close();
private:
	sqlite3 *db;
	sqlite3_stmt *stmt;
};

#endif /* VDSQLITE_H_ */
