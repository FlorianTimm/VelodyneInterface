/*
 * VdFile.cpp
 *
 *  Created on: 26.11.2017
 *      Author: timm
 */
#include <string>
#include <iostream>
#include <list>
using namespace std;
#include "VdFile.h"

list<VdPoint>& VdFile::getWritingQueue() {
	/*
	 Returns points in queue
	 :return: points in queue
	 :rtype: VdPoint[]
	 */
	return this->writingQueue;
}

void VdFile::clearWritingQueue() {
	// clears writing queue
	this->writingQueue.clear();
}

inline bool ends_with(string const & value, string const & ending) {
	if (ending.size() > value.size())
		return false;
	return equal(ending.rbegin(), ending.rend(), value.rbegin());
}

string VdFile::makeFilename(string file_format, string file_name) {
	/*
	 generates a new file_name from timestamp
	 :param file_format: file suffix
	 :type file_format: str
	 :return: string with date and suffix
	 :rtype: str
	 */
	string file_ending = string(".") + file_format;
	if (file_name.empty()) {
		return (string("noname") + file_ending);
	} else if (ends_with(file_name, file_ending)) {
		return file_name;
	}
	return file_name + file_ending;
}

void VdFile::writeData(list<VdPoint>* dataset) {
	/*
	 adds data and writes it to file
	 :param data: ascii data to write
	 :type data: VdPoint[]
	 */
	this->addDataset(dataset);
	this->write();
}

void VdFile::addPoint(VdPoint point) {
	/*
	 Adds a point to write queue
	 :param p: point
	 :type p: VdPoint
	 */
	this->writingQueue.push_back(point);
}

void VdFile::addDataset(list<VdPoint>* dataset) {
	/*
	 adds multiple points to write queue
	 :param dataset: multiple points
	 :type dataset: VdPoint[]
	 */
	cout << dataset->size() << " datasets added" << endl;

	VdPoint p (1,2,3,4,5);

	//this->writingQueue.push_back(p);

	this->writingQueue.insert(this->writingQueue.begin(), dataset->begin(), dataset->end());

	cout << this->writingQueue.size();
	cout << " datasets" << endl;
}

