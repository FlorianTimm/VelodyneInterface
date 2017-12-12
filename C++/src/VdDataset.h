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
#include "iniparser/iniparser.h"

class VdDataset {
public:
	VdDataset(dictionary * conf, char * dataset);
	void convertData();
	const std::list<VdPoint>& getData() const;

private:
	std::list<VdPoint> data;
	double getAzimuth(int);
	double getTime();
	bool isDualReturn();
	void getAzimuths(double[], double[]);

	char * dataset;
	dictionary * conf;
	int verticalAngle[16] = { -15, 1, -13, 3, -11, 5, -9, 7, -7, 9, -5, 11, -3,
			13, -1, 15 };
	double tRepeat;
	int offsets[12] = { 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
			1100 };

};
#endif /* VDDATASET_H_ */
