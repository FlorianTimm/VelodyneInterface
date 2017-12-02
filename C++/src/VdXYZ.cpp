/*!
 *  \brief		represents a coordinate
 *
 *  \author		Florian Timm
 *  \version	2017.11.30
 *  \copyright	MIT License
 */

#include "VdXYZ.h"

VdXYZ::VdXYZ() {
	/** constructor */
	this->x_ = -999;
	this->y_ = -999;
	this->z_ = -999;
}

VdXYZ::VdXYZ(double x, double y, double z) {
	/**
	 * constructor
	 * @param x x coordinate
	 * @param y y coordinate
	 * @param z z coordinate
	 */
	this->x_ = x;
	this->y_ = y;
	this->z_ = z;
}

VdXYZ::~VdXYZ() {
	/** destructor stub */
}

double VdXYZ::getX() {
	/**
	 * returns x coordinate
	 * @return x coordinate
	 */
	return (x_);
}

void VdXYZ::setX(double x) {
	/**
	 * sets x coordinate
	 * @param x x coordinate
	 */
	this->x_ = x;
}

double VdXYZ::getY() {
	/**
	 * returns y coordinate
	 * @return y coordinate
	 */
	return (y_);
}

void VdXYZ::setY(double y) {
	/**
	 * sets y coordinate
	 * @param y y coordinate
	 */
	this->y_ = y;
}

double VdXYZ::getZ() {
	/**
	 * returns z coordinate
	 * @return z coordinate
	 */
	return (z_);
}

void VdXYZ::setZ(double z) {
	/**
	 * sets z coordinate
	 * @param z z coordinate
	 */
	this->z_ = z;
}
