/*
 * main.cpp
 *
 *  Created on: 27.11.2017
 *      Author: timm
 */

#include <iostream>
#include <fstream>
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

void transformBin2x(std::string binFile, VdFile* newFile) {
	clock_t start_t;
	float elapsed;

	start_t = clock();

	fstream file(binFile, std::fstream::binary | std::fstream::in);

	if (file.is_open()) {
		file.seekg(0, ios::end);
		int length = file.tellg();
		file.seekg(0, ios::beg);

		cout << "FileSize: " << length << endl;
		int cntDatasets = (int) (length / 1206);
		cout << "DataSets: " << cntDatasets << endl;

		for (int i = 0; i < cntDatasets; i++) {

			//while (!file.eof()) {
			char * dataset = new char[1206];
			file.read(dataset, 1206);
			VdDataset vd = VdDataset(dataset);
			vd.convertData();

			std::list<VdPoint> p = vd.getData();
			newFile->addDataset(&p);
		}
		newFile->write();
	}
	file.close();

	elapsed = (float) (clock() - start_t) / CLOCKS_PER_SEC;

	cout << "Zeitbedarf: " << elapsed << endl;
}

void start(string old_end, string filename_old, string new_end,
		string filename_new) {
	if (old_end == "bin") {
		cout << "Input: bin" << endl;
		cout << "Output: ";
		if (new_end == "txt") {
			cout << "txt" << endl;
			VdTxtFile txt(filename_new);
			transformBin2x(filename_old, &txt);
		} else if (new_end == "xyz") {
			cout << "xyz" << endl;
			VdXYZFile xyz = VdXYZFile(filename_new);
			transformBin2x(filename_old, &xyz);
		} else if (new_end == "obj") {
			cout << "obj" << endl;
			VdObjFile obj = VdObjFile(filename_new);
			transformBin2x(filename_old, &obj);
		} else if (new_end == "sql") {
			cout << "sql" << endl;
			VdSQLite sql = VdSQLite(filename_new);
			transformBin2x(filename_old, &sql);
		} else {
			cout << "unknown file format" << endl;
		}

	} else if (old_end == "txt") {
		cout << "not implemented!" << endl;
	} else {
		cout << "unknown file format" << endl;
	}
}

int main(int argc, char* argv[]) {
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
		cout << "usage: veloTrans [bin|txt] old_file [txt|xyz|obj|sql] new_file"
				<< endl;
	}
	return 0;
}
