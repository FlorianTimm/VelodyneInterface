/*
 * VdPoint.cpp
 *
 *  Created on: 26.11.2017
 *      Author: timm
 */

#include <math.h>
#include <vector>
#include <iostream>
#include "VdXYZ.h"
#include "VdPoint.h"
#define PI 3.141592653589793238463

VdPoint::VdPoint() {
	time_ = 0;
	azimuth_ = 0;
	vertical_ = 0;
	distance_ = 0;
	reflection_ = 0;
}

VdPoint::VdPoint(double time, double azimuth, int verticalAngle, double distance,
		int reflection) {
	// TODO Auto-generated constructor stub
	time_ = time;
	azimuth_ = azimuth;
	vertical_ = verticalAngle;
	distance_ = distance;
	reflection_ = reflection;
}

double VdPoint::dRho = PI / 180.0;

VdPoint::~VdPoint() {
	// TODO Auto-generated destructor stub
}

double VdPoint::deg2rad(double degree) {
	/*
	 converts degree to radians
	 :param degree: degrees
	 :type degree: double
	 :return: radians
	 :rtype: double
	 */
	return degree * dRho;
}

VdXYZ VdPoint::getXYZ() {
	/*
	 Gets local coordinates
	 :return: local coordinates x, y, z in metres
	 :rtype: double, double, double
	 */
	double beam_center = 0.04191;

	// slope distance to beam center
	double d = distance_ - beam_center;

	// vertical angle in radians
	double v = deg2rad(vertical_);

	// azimuth in radians
	double a = deg2rad(azimuth_);

	// horizontal distance
	double s = d * cos(v) + beam_center;

	double x = s * sin(a);
	double y = s * cos(a);
	double z = d * sin(v);

	return VdXYZ(x,y,z);
}

double VdPoint::getAzimuth() {
	return azimuth_;
}

void VdPoint::setAzimuth(double azimuth) {
	this->azimuth_ = azimuth;
}

double VdPoint::getDistance() {
	return distance_;
}

void VdPoint::setDistance(double distance) {
	this->distance_ = distance;
}

int VdPoint::getReflection() {
	return reflection_;
}

void VdPoint::setReflection(int reflection) {
	this->reflection_ = reflection;
}

double VdPoint::getTime() {
	return time_;
}

void VdPoint::setTime(double time) {
	this->time_ = time;
}

int VdPoint::getVertical() {
	return vertical_;
}

void VdPoint::setVertical(int vertical) {
	this->vertical_ = vertical;
}
