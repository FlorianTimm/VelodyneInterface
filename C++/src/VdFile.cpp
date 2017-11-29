/*!
 *  \brief		class for writing data
 *
 *  \author		Florian Timm
 *  \version	2017.11.29
 *  \copyright	MIT License
 */
#include <string>
#include <iostream>
#include <list>
using namespace std;
#include "VdFile.h"

list<VdPoint>& VdFile::getWritingQueue() {
	/**
	 * Returns points in queue
	 * @return points in queue
	 */
	return this->writingQueue;
}

void VdFile::clearWritingQueue() {
	/** clears writing queue */
	this->writingQueue.clear();
}

inline bool ends_with(string const & value, string const & ending) {
	if (ending.size() > value.size())
		return (false);
	return (equal(ending.rbegin(), ending.rend(), value.rbegin()));
}

string VdFile::makeFilename(string file_format, string file_name) {
	/**
	 * generates a new file_name from timestamp
	 * @param file_format file suffix
	 * @param file_name file name
	 * @return string with date and suffix
	 */
	string file_ending = string(".") + file_format;
	if (file_name.empty()) {
		return (string("noname") + file_ending);
	} else if (ends_with(file_name, file_ending)) {
		return (file_name);
	}
	return (file_name + file_ending);
}

void VdFile::writeData(list<VdPoint>* dataset) {
	/**
	 * adds data and writes it to file
	 * @param data ascii data to write
	 */
	this->addDataset(dataset);
	this->write();
}

void VdFile::addPoint(VdPoint point) {
	/**
	 * Adds a point to write queue
	 * @param p point
	 */
	this->writingQueue.push_back(point);
}

void VdFile::addDataset(list<VdPoint>* dataset) {
	/**
	 * adds multiple points to write queue
	 * @param dataset multiple points
	 */
	this->writingQueue.insert(this->writingQueue.begin(), dataset->begin(), dataset->end());
}

