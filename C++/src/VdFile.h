/*
 * VdFile.h
 *
 *  Created on: 26.11.2017
 *      Author: timm
 */

#ifndef VDFILE_H_
#define VDFILE_H_

#include <vector>
#include <string>
#include "VdFile.h"
#include "VdPoint.h"

class VdFile {
public:
	virtual ~VdFile();
	std::vector<VdPoint>& getWritingQueue();
	void clearWritingQueue();
	std::string makeFilename (std::string file_format, std::string file_name=std::string(""));
	void addPoint(VdPoint point);
	void addDataset(std::vector<VdPoint>* dataset);
	void writeData(std::vector<VdPoint>* data);
	virtual void write() = 0;

protected:
	virtual void open(std::string filename) = 0;
	virtual void close() = 0;
	std::vector<VdPoint> writingQueue_;
};

#endif /* VDFILE_H_ */
