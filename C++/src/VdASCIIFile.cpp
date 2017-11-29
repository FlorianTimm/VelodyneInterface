/*!
 *  \brief		class for writing data to ascii file
 *
 *  \author		Florian Timm
 *  \version	2017.11.29
 *  \copyright	MIT License
 */

#include <string>
#include <vector>
#include <fstream>
#include <iostream>
using namespace std;
#include "VdPoint.h"
#include "VdASCIIFile.h"

void VdASCIIFile::openASCII(string filename, string file_format) {
	/**
	 * opens ascii file for writing
	 * @param filename file name
	 */
	filename = this->makeFilename(file_format, filename);
	this->file_.open(filename, std::fstream::out | std::fstream::app);
}

void VdASCIIFile::write2file(string data) {
	/**
	 * writes ascii data to file
	 * @param data: data to write
	 */
	//std::cout << data.c_str() << std::endl;
	this->file_ << data.c_str();
}

void VdASCIIFile::write() {
	/** writes data to file */
	string txt;
	for (VdPoint p : this->writingQueue)
		txt += this->format(p);
	this->write2file(txt);
	this->clearWritingQueue();
}

void VdASCIIFile::close() {
	/** close file */
	this->file_.close();
}

