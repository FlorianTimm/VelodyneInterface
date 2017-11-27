/*
 * VdXYZ.cpp
 *
 *  Created on: 26.11.2017
 *      Author: timm
 */

#include "VdXYZ.h"

VdXYZ::VdXYZ() {
	// TODO Auto-generated constructor stub
	this->x_ = -999;
	this->y_ = -999;
	this->z_ = -999;
}

VdXYZ::VdXYZ(double x, double y, double z) {
	// TODO Auto-generated constructor stub
	this->x_ = x;
	this->y_ = y;
	this->z_ = z;
}

VdXYZ::~VdXYZ() {
	// TODO Auto-generated destructor stub
}

double VdXYZ::getX() {
	return x_;
}

void VdXYZ::setX(double x) {
	this->x_ = x;
}

double VdXYZ::getY() {
	return y_;
}

void VdXYZ::setY(double y) {
	this->y_ = y;
}

double VdXYZ::getZ() {
	return z_;
}

void VdXYZ::setZ(double z) {
	this->z_ = z;
}
