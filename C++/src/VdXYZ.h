/*
 * VdXYZ.h
 *
 *  Created on: 26.11.2017
 *      Author: timm
 */

#ifndef VDXYZ_H_
#define VDXYZ_H_

class VdXYZ {
public:
	VdXYZ();
	VdXYZ(double x, double y, double z);
	virtual ~VdXYZ();
	double getX();
	void setX(double x);
	double getY();
	void setY(double y);
	double getZ();
	void setZ(double z);

private:
	double x_;
	double y_;
	double z_;
};

#endif /* VDXYZ_H_ */
