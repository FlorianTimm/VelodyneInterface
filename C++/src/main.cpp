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
using namespace std;
#include "VdXYZ.h"
#include "VdPoint.h"
#include "VdDataset.h"
#include "VdObjFile.h"

int main() {
	char * dataset;

	cout << "main" << endl;
	clock_t start_t;
	float elapsed;

	start_t = clock();

	ifstream file("/ssd/daten/ThesisMessung/tief5_bin/0.bin", ios::binary);

	VdObjFile obj = VdObjFile(
			"/ssd/daten/ThesisMessung/tief5_bin/test_cpp.obj");

	if (file.is_open()) {
		while (!file.eof()) {
			dataset = new char[1206];
			file.read(dataset, 1206);
			VdDataset vd = VdDataset(dataset);
			vd.convertData();
			//cout << "Punkte: " << vd.getData().size() << endl;
			std::vector<VdPoint> p;
			p = vd.getData();
			//p.reserve(4);
			//p.push_back(VdPoint (1,2,3,4,5));
			obj.addDataset(&p);
//			for (VdPoint p : vd.getData()) {
//				cout << p.getTime() << " " << p.getAzimuth() << " "
//						<< p.getVertical() << " " << p.getDistance() << endl;
//			}
		}
		obj.write();
	}
	file.close();
	elapsed = (float) (clock() - start_t) / CLOCKS_PER_SEC;

	cout << "Zeitbedarf: " << elapsed  << endl;
}
