/*!
 *  \brief		class for writing data to sqlite database
 *
 *  \author		Florian Timm
 *  \version	2017.11.29
 *  \copyright	MIT License
 */

#ifndef VDSQLITEXYZ_H_
#define VDSQLITEXYZ_H_

#include "VdFile.h"
#include <sqlite3.h>
#include <string>
using namespace std;

class VdSQLiteXYZ: public VdFile {
public:
	VdSQLiteXYZ(string filename = "");
	void write();
protected:
	void open(std::string filename = "");
	void close();
private:
	sqlite3 *db;
	sqlite3_stmt *stmt;
};

#endif /* VDSQLITEXYZ_H_ */
