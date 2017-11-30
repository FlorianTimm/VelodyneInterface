/*!
 *  \brief		represents a file for writing data
 *
 *  \author		Florian Timm
 *  \version	2017.11.30
 *  \copyright	MIT License
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
