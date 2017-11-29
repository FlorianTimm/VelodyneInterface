/*
 * VdXYZFile.h
 *
 *  Created on: 28.11.2017
 *      Author: timm
 */

#ifndef VDXYZFILE_H_
#define VDXYZFILE_H_

#include <string>
#include "VdASCIIFile.h"
using namespace std;

class VdXYZFile: public VdASCIIFile {
public:
	VdXYZFile(string filename = "");

protected:
	void open(string filename);
	string format(VdPoint point);
};

#endif /* VDXYZFILE_H_ */
