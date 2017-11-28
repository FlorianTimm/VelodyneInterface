/*
 * main.cpp
 *
 *  Created on: 27.11.2017
 *      Author: timm
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <iterator>
#include <string>
using namespace std;
#include "VdXYZ.h"
#include "VdPoint.h"
#include "VdDataset.h"
#include "VdFile.h"
#include "VdObjFile.h"

void transformBin2Obj(std::string binFile, std::string objFile) {
	char * dataset;

	cout << "main" << endl;
	clock_t start_t;
	float elapsed;

	start_t = clock();

	ifstream file(binFile, ios::binary | ios::in);

	VdObjFile obj = VdObjFile(objFile);

	if (file.is_open()) {
		file.seekg(0, ios::end);
		int length = file.tellg();
		file.seekg(0, ios::beg);

		cout << "FileSize: " << length << endl;
		int cntDatasets = (int) (length / 1206);
		cout << "DataSets: " << cntDatasets << endl;

		for (int i = 0; i < cntDatasets; i++) {
			//while (!file.eof()) {
			dataset = new char[1206];
			file.read(dataset, 1206);
			VdDataset vd = VdDataset(dataset);
			vd.convertData();
			//cout << "Punkte: " << vd.getData().size() << endl;
			std::vector<VdPoint> p = vd.getData();
			obj.addDataset(&p);
		}
		obj.write();
	}
	file.close();
	elapsed = (float) (clock() - start_t) / CLOCKS_PER_SEC;

	cout << "Zeitbedarf: " << elapsed << endl;
}

void start (string old_end, string filename_old, string new_end, string filename_new) {
	if (old_end == "bin")
	{
		if (new_end == "txt") {}
		else if (new_end == "xyz") {}
		else if (new_end == "obj") {
			transformBin2Obj(filename_old, filename_new);
		}
		else if (new_end == "sql") {}
	}
	else if (old_end == "txt")
	{
		if (new_end == "xyz") {}
		else if (new_end == "obj") {}
		else if (new_end == "sql") {}
	}
}

int main(int argc, char* argv[]) {
	if (argc == 3) {
		string filename_old = argv[1];
		string filename_new = argv[2];
		string old_end = filename_old.substr( filename_old.length() - 3 );
		string new_end = filename_new.substr( filename_new.length() - 3 );
		//transformBin2Obj(argv[1], argv[2]);
		start(old_end, filename_old, new_end, filename_new);

	} else if (argc == 5) {
		start(argv[1], argv[2], argv[3], argv[4]);
	} else {
		cout << "No parameters!" << endl;
		cout << "usage: veloTrans bin|txt old_file txt|xyz|obj|sql new_file" << endl;
		cout << "usage: veloTrans old_file new_file" << endl;
	}
	return 0;
}
