/*
 * VdASCIIFile.h
 *
 *  Created on: 26.11.2017
 *      Author: timm
 */

#ifndef VDASCIIFILE_H_
#define VDASCIIFILE_H_

#include "VdFile.h"
#include <fstream>

class VdASCIIFile : public VdFile {
public:
	void write();

protected:
	void openASCII(std::string filename, std::string file_format);
	void write2file(std::string data);
	void close();
	virtual std::string format(VdPoint point) = 0;

private:
	std::ofstream file_;
};

#endif /* VDASCIIFILE_H_ */
