/*
 * VdTxtFile.h
 *
 *  Created on: 27.11.2017
 *      Author: timm
 */

#ifndef VDTXTFILE_H_
#define VDTXTFILE_H_

#include <string>
#include "VdASCIIFile.h"
#include "VdPoint.h"
using namespace std;

class VdTxtFile: public VdASCIIFile {
public:
	VdTxtFile(string filename = "");

protected:
	void open (string filename = "");
	string format(VdPoint);
};

#endif /* VDTXTFILE_H_ */
