/*
 * VdTxtFile.h
 *
 *  Created on: 27.11.2017
 *      Author: timm
 */

#ifndef VDTXTFILE_H_
#define VDTXTFILE_H_

#include "VdASCIIFile.h"

class VdTxtFile: public VdASCIIFile {
public:
	VdTxtFile();
	virtual ~VdTxtFile();
};

#endif /* VDTXTFILE_H_ */
