/*!
 *  \brief		class for writing data to xyz file
 *
 *  \author		Florian Timm
 *  \version	2017.11.30
 *  \copyright	MIT License
 */

#include "VdXYZFile.h"
#include <string>
#include <iostream>
using namespace std;

VdXYZFile::VdXYZFile(string filename) {
	/**
	 * construktor
	 * @param filename name for new file
	 */
	this->open(filename);
	this->writingQueue = list<VdPoint>();
}

void VdXYZFile::open(string filename = "") {
	/**
	 * opens a txt file for writing
	 * @param filename name and path to new file
	 */
	openASCII(filename, "xyz");
}

string VdXYZFile::format(VdPoint point) {
	/**
	 * Formats point for OBJ
	 * @param point VdPoint
	 * @return obj point string
	 */
	VdXYZ xyz = point.getXYZ();
	// '{:.3f} {:.3f} {:.3f}\n'
	char result[50];
	sprintf(result, "%.3f %.3f %.3f\n", xyz.getX(), xyz.getY(), xyz.getZ());
	//cout << result;
	return (string(result));
}
