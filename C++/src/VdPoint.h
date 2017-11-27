/*
 * VdPoint.h
 *
 *  Created on: 26.11.2017
 *      Author: timm
 */

#ifndef VDPOINT_H_
#define VDPOINT_H_
#include "VdXYZ.h"

class VdPoint {
public:
	VdPoint();
	VdPoint(double, double, int, double, int);
	virtual ~VdPoint();
	static double deg2rad(double degree);
	VdXYZ getXYZ();
	double getAzimuth();
	void setAzimuth(double azimuth);
	double getDistance();
	void setDistance(double distance);
	int getReflection();
	void setReflection(int reflection);
	double getTime();
	void setTime(double time);
	int getVertical();
	void setVertical(int vertical);
	static double dRho;

private:
	double time_;
	double azimuth_;
	int vertical_;
	double distance_;
	int reflection_;
};

#endif /* VDPOINT_H_ */
