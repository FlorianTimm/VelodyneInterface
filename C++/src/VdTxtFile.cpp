/*
 * VdTxtFile.cpp
 *
 *  Created on: 27.11.2017
 *      Author: timm
 */

#include "VdTxtFile.h"
#include <string>
using namespace std;

VdTxtFile::VdTxtFile(string filename) {
	// TODO Auto-generated constructor stub
	this->open(filename);
}

void VdTxtFile::open(std::string filename) {
	/*
	 opens a txt file for writing
	 :param filename: name and path to new file
	 :type filename: str
	 */
	this->openASCII(filename, string("txt"));
}

string VdTxtFile::format(VdPoint point) {
	/*
	 Formats point for Txt
	 :param point: VdPoint
	 :type point: VdPoint
	 :return: txt point string
	 :rtype: str
	 */
	VdXYZ xyz = point.getXYZ();
	// '{:012.1f}\t{:07.3f}\t{: 03.0f}\t{:06.3f}\t{:03.0f}\n'
	char result[40];
	sprintf (result, "%012.1f\t%07.3f\t%03d\t%06.3f\t%03d\n", point.getTime(), point.getAzimuth(), point.getVertical(), point.getDistance(), point.getReflection());
	return string(result);
}
