/*!
 *  \brief		class for writing raw data to txt file
 *
 *  \author		Florian Timm
 *  \version	2017.11.29
 *  \copyright	MIT License
 */

#include "VdTxtFile.h"
#include <string>
using namespace std;

VdTxtFile::VdTxtFile(string filename) {
	/**
	 * constructor
	 * @param filename: name and path to new file
	 */
	this->open(filename);
}

void VdTxtFile::open(std::string filename) {
	/**
	 * opens a txt file for writing
	 * @param filename: name and path to new file
	 */
	this->openASCII(filename, string("txt"));
}

string VdTxtFile::format(VdPoint point) {
	/**
	 * Formats point for Txt
	 * @param point: VdPoint
	 * @return txt point string
	 */
	VdXYZ xyz = point.getXYZ();
	char result[40];
	sprintf(result, "%012.1f\t%07.3f\t%03d\t%06.3f\t%03d\n", point.getTime(),
			point.getAzimuth(), point.getVertical(), point.getDistance(),
			point.getReflection());
	return (string(result));
}
