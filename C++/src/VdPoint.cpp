/*!
 *  \brief		represents a point
 *
 *  \author		Florian Timm
 *  \version	2017.11.30
 *  \copyright	MIT License
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

VdPoint::VdPoint(double time, double azimuth, int verticalAngle,
		double distance, int reflection) {
	/**
	 * Constructor
	 * @param time recording time in microseconds
	 * @param azimuth Azimuth direction in degrees
	 * @param vertical Vertical angle in degrees
	 * @param distance distance in metres
	 * @param reflection reflection 0-255
	 */
	time_ = time;
	azimuth_ = azimuth;
	vertical_ = verticalAngle;
	distance_ = distance;
	reflection_ = reflection;
}

double VdPoint::dRho = PI / 180.0;

VdPoint::~VdPoint() {
	/** destructor stub */
}

double VdPoint::deg2rad(double degree) {
	/**
	 * converts degree to radians
	 * @param degree degrees
	 * @return radians
	 */
	return degree * dRho;
}

VdXYZ VdPoint::getXYZ() {
	/**
	 * Gets local coordinates
	 * @return local coordinates x, y, z in metres
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

	return VdXYZ(x, y, z);
}

double VdPoint::getAzimuth() {
	/**
	 * returns azimuth
	 * @return azimuth in degrees
	 */
	return (azimuth_);
}

double VdPoint::getDistance() {
	/**
	 * returns the distance
	 * @return distance
	 */
	return (distance_);
}

int VdPoint::getReflection() {
	/**
	 * returns the reflection
	 * @return reflection between 0 - 255
	 */
	return (reflection_);
}

double VdPoint::getTime() {
	/**
	 * returns time
	 * @return time in microseconds
	 */
	return (time_);
}

int VdPoint::getVertical() {
	/**
	 * returns the vertical angle
	 * @return vertical angle in degrees
	 */
	return (vertical_);
}
