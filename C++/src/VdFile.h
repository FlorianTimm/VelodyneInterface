/*
 * VdFile.h
 *
 *  Created on: 26.11.2017
 *      Author: timm
 */

#ifndef VDFILE_H_
#define VDFILE_H_

#include <list>
#include <string>
#include "VdFile.h"
#include "VdPoint.h"

class VdFile {
public:
	std::list<VdPoint>& getWritingQueue();
	void clearWritingQueue();
	std::string makeFilename (std::string file_format, std::string file_name=std::string(""));
	void addPoint(VdPoint point);
	void addDataset(std::list<VdPoint>* dataset);
	void writeData(std::list<VdPoint>* data);
	virtual void write() = 0;

protected:
	virtual void open(std::string filename = "") = 0;
	virtual void close() = 0;
	std::list<VdPoint> writingQueue;
};


#endif /* VDFILE_H_ */
