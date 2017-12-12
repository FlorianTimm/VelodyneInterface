/*!
 *  \brief		class for writing data to ascii file
 *
 *  \author		Florian Timm
 *  \version	2017.11.29
 *  \copyright	MIT License
 */

#ifndef VDASCIIFILE_H_
#define VDASCIIFILE_H_

#include "VdFile.h"
#include <fstream>

class VdASCIIFile: public VdFile {
public:
	void write();
protected:
	void openASCII(std::string filename, std::string file_format);
	void write2file(std::string data);
	void close();
	virtual std::string format(VdPoint point) = 0;

	FILE* file;
};

#endif /* VDASCIIFILE_H_ */
