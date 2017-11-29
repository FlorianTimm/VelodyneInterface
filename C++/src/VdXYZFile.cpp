/*
 * VdXYZFile.cpp
 * creates and fills an xyz-file
 *
 *  Created on: 28.11.2017
 *      Author: timm
 */

#include "VdXYZFile.h"
#include <string>
#include <iostream>
using namespace std;

VdXYZFile::VdXYZFile(string filename) {
	// TODO Auto-generated constructor stub
	this->open(filename);
	this->writingQueue = list<VdPoint>();
}

void VdXYZFile::open(string filename = "") {
	/*
	 opens a txt file for writing
	 :param filename: name and path to new file
	 :type filename: str
	 */
	openASCII(filename, "xyz");
}

string VdXYZFile::format(VdPoint point) {
	/*
	 Formats point for OBJ
	 :param point: VdPoint
	 :type point: VdPoint
	 :return: obj point string
	 :rtype: str
	 */
	VdXYZ xyz = point.getXYZ();
	// '{:.3f} {:.3f} {:.3f}\n'
	char result[50];
	sprintf(result, "%.3f %.3f %.3f\n", xyz.getX(), xyz.getY(), xyz.getZ());
	//cout << result;
	return string(result);
}