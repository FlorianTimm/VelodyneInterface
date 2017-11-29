/*
 * VdASCIIFile.cpp
 *
 *  Created on: 26.11.2017
 *      Author: timm
 */

#include <string>
#include <vector>
#include <fstream>
#include <iostream>
using namespace std;
#include "VdPoint.h"
#include "VdASCIIFile.h"

void VdASCIIFile::openASCII(string filename, string file_format) {
	/*
	 opens ascii file for writing
	 :param filename: file name
	 :type filename: str
	 */
	filename = this->makeFilename(file_format, filename);
	this->file_.open(filename, std::fstream::out | std::fstream::app);
}

void VdASCIIFile::write2file(string data) {
	/*
	 writes ascii data to file
	 :param data: data to write
	 :type data: str
	 */
	//std::cout << data.c_str() << std::endl;
	this->file_ << data.c_str();
}

void VdASCIIFile::write() {
	// writes data to file
	string txt;
	for (VdPoint p : this->writingQueue)
		txt += this->format(p);
	this->write2file(txt);
	this->clearWritingQueue();
}

void VdASCIIFile::close() {
	// close file
	this->file_.close();
}

