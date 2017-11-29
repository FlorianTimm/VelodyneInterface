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
#include "VdObjFile.h"

VdObjFile::VdObjFile(string filename) {
	// TODO Auto-generated constructor stub
	this->open(filename);
}

void VdObjFile::open(std::string filename) {
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
	char result[50];
	sprintf (result, "v %.3f %.3f %.3f\n", xyz.getX(), xyz.getY(), xyz.getZ());
	return string(result);
}

