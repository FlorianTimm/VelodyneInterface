/*!
 *  \brief		main method
 *
 *  \author		Florian Timm
 *  \version	2017.11.29
 *  \copyright	MIT License
 */

#include <iostream>
#include <stdio.h>
#include <list>
#include <iterator>
#include <string>
using namespace std;
#include "VdXYZ.h"
#include "VdPoint.h"
#include "VdDataset.h"
#include "VdFile.h"
#include "VdXYZFile.h"
#include "VdTxtFile.h"
#include "VdObjFile.h"
#include "VdSQLite.h"
#include "VdSQLiteXYZ.h"
extern "C" {
#include "iniparser/iniparser.h"
}

dictionary * ini = NULL;

void loadini() {
	ini = iniparser_load("config.ini");
}

void transformBin2x(std::string binFile, VdFile* newFile) {
	/**
	 * transforms bin files to several
	 file formats
	 * @param binFile bin file
	 * @param newFile file object to write
	 */

	ifstream file(binFile.c_str(), ios::binary | ios::in);

	if (file.is_open()) {
		file.seekg(0, ios::end);
		int length = file.tellg();
		file.seekg(0, ios::beg);

		cout << "FileSize: " << length << endl;
		int cntDatasets = (int) (length / 1206);
		cout << "DataSets: " << cntDatasets << endl;

		for (int i = 0; i < cntDatasets; i++) {

			//while (!file.eof()) {
			char dataset[1206];
			file.read(dataset, 1206);
			VdDataset vd = VdDataset(ini, dataset);
			vd.convertData();

			std::list<VdPoint> p = vd.getData();
			newFile->addDataset(&p);
		}
		newFile->write();
	}
	file.close();
}

void start(string old_format, string filename_old, string new_format,
		string filename_new) {
	/**
	 * transforms files
	 * @param old_format format of input file (bin, txt)
	 * @param filename_old name of input file
	 * @param new_format format of output file (txt, xyz, obj, sql, sqlxyz)
	 * @param filename_new name of output file
	 */
	if (old_format == "bin") {
		cout << "Input: bin" << endl;
		cout << "Output: ";
		if (new_format == "txt") {
			cout << "txt" << endl;
			VdTxtFile txt(filename_new);
			transformBin2x(filename_old, &txt);
		} else if (new_format == "xyz") {
			cout << "xyz" << endl;
			VdXYZFile xyz = VdXYZFile(filename_new);
			transformBin2x(filename_old, &xyz);
		} else if (new_format == "obj") {
			cout << "obj" << endl;
			VdObjFile obj = VdObjFile(filename_new);
			transformBin2x(filename_old, &obj);
		} else if (new_format == "sql") {
			cout << "sql" << endl;
			VdSQLite sql = VdSQLite(filename_new);
			transformBin2x(filename_old, &sql);
		} else if (new_format == "sqlxyz") {
			cout << "sqlxyz" << endl;
			VdSQLiteXYZ sqlxyz = VdSQLiteXYZ(filename_new);
			transformBin2x(filename_old, &sqlxyz);
		} else {
			cout << "unknown file format" << endl;
		}

	} else if (old_format == "txt") {
		cout << "not implemented!" << endl;
	} else {
		cout << "unknown file format" << endl;
	}
}

int main(int argc, char* argv[]) {
	/**
	 * main method, starts program
	 * @param argc number of arguments
	 * @param argv arguments
	 * @return 0
	 */

	loadini();

	if (argc == 3) {
		string filename_old = argv[1];
		string filename_new = argv[2];
		string old_end = filename_old.substr(filename_old.length() - 3);
		string new_end = filename_new.substr(filename_new.length() - 3);
		//transformBin2Obj(argv[1], argv[2]);
		start(old_end, filename_old, new_end, filename_new);

	} else if (argc == 5) {
		start(argv[1], argv[2], argv[3], argv[4]);
	} else {
		cout << "No parameters!" << endl;
		cout << "usage: veloTrans [bin|txt] old_file [txt|xyz|obj|sql|sqltxt] new_file"
				<< endl;
	}
	return (0);
}
