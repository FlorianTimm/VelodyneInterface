/*
 * VdObjFile.h
 *
 *  Created on: 26.11.2017
 *      Author: timm
 */

#ifndef VDOBJFILE_H_
#define VDOBJFILE_H_

#include "VdASCIIFile.h"

class VdObjFile: public VdASCIIFile {
public:
	VdObjFile(std::string filename = "");

protected:
	void open(std::string filename = "");
	string format(VdPoint point);
};

#endif /* VDOBJFILE_H_ */
