/*!
 *  \brief		represents a file for writing data
 *
 *  \author		Florian Timm
 *  \version	2017.11.30
 *  \copyright	MIT License
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
	/**
	 * opens a txt file for writing
	 * @param filename name and path to new file
	 */
	this->openASCII(filename, string("obj"));
}

string VdObjFile::format(VdPoint point) {
	/**
	 * Formats point for OBJ
	 * @param point VdPoint
	 * @return obj point string
	 */
	VdXYZ xyz = point.getXYZ();
	char result[50];
	sprintf(result, "v %.3f %.3f %.3f\n", xyz.getX(), xyz.getY(), xyz.getZ());
	return (string(result));
}

