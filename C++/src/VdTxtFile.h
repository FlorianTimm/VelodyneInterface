/*!
 *  \brief		class for writing raw data to txt file
 *
 *  \author		Florian Timm
 *  \version	2017.11.29
 *  \copyright	MIT License
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
