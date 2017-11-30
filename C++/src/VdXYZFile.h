/*!
 *  \brief		class for writing data to xyz file
 *
 *  \author		Florian Timm
 *  \version	2017.11.30
 *  \copyright	MIT License
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
