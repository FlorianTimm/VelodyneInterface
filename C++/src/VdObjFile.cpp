/*
 * VdObjFile.cpp
 *
 *  Created on: 26.11.2017
 *      Author: timm
 */

#include <string>
#include <vector>
#include <fstream>
using namespace std;
#include "VdXYZ.h"
#include "VdPoint.h"
#include "VdObjFile.h"

VdObjFile::VdObjFile() {
	// TODO Auto-generated constructor stub
}

VdObjFile::VdObjFile(string filename) {
	// TODO Auto-generated constructor stub
	vector<VdPoint> writingQueue_;
	this->open(filename);
}

void VdObjFile::open(string filename) {
	/*
	 opens a txt file for writing
	 :param filename: name and path to new file
	 :type filename: str
	 */
	this->openASCII(filename, string("obj"));
}

string VdObjFile::format(VdPoint point) {
	/*
	 Formats point for OBJ
	 :param p: VdPoint
	 :type p: VdPoint
	 :return: obj point string
	 :rtype: str
	 */
	VdXYZ xyz = point.getXYZ();
	// 'v {:.3f} {:.3f} {:.3f}\n'
	string result = string("v ");
	result += to_string(xyz.getX()) + " ";
	result += to_string(xyz.getY()) + " ";
	result += to_string(xyz.getZ()) + "\n";
	return result;
}

