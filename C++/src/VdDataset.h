/*!
 *  \brief		represents a dataset
 *
 *  \author		Florian Timm
 *  \version	2017.11.30
 *  \copyright	MIT License
 */

#ifndef VDDATASET_H_
#define VDDATASET_H_

#include "VdPoint.h"
#include <list>

class VdDataset {
public:
	VdDataset(char dataset[]);
	void convertData();
	const std::list<VdPoint>& getData() const;

private:
	std::list<VdPoint> data;
	double getAzimuth(int);
	double getTime();
	bool isDualReturn();
	void getAzimuths(double[], double[]);

	char * dataset;
	static const int verticalAngle[16];
	static const double tRepeat;
	static const int offsets[12];

};
#endif /* VDDATASET_H_ */
