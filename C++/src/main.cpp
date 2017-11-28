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

int main(int argc, char* argv[]) {
	if (argc >= 3) {
		transformBin2Obj(argv[1], argv[2]);
	} else {
		cout << "Keine Dateien übergeben" << endl;
	}
	return 0;
}
