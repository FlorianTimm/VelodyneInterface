/*
 * VdDataset.cpp
 *
 *  Created on: 26.11.2017
 *      Author: Florian Timm
 */

//#include </usr/include/python3.6m/Python.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <iterator>
using namespace std;
#include "VdXYZ.h"
#include "VdPoint.h"
#include "VdDataset.h"

VdDataset::VdDataset(char dataset[]) {
	this->dataset = dataset;
	vector<VdPoint> data;
	data.reserve(384);
}

const int VdDataset::verticalAngle[16] = { -15, 1, -13, -3, -11, 5, -9, 7, -7,
		9, -5, 11, -3, 13, -1, 15 };
const double VdDataset::tRepeat = 55.296;
const int VdDataset::offsets[12] = { 0, 100, 200, 300, 400, 500, 600, 700, 800,
		900, 1000, 1100 };

double VdDataset::getAzimuth(int block) {
	/*
	 gets azimuth of a data block
	 :param block: number of data block
	 :type block: int
	 :return: azimuth
	 :rtype: double
	 */

	int offset = this->offsets[block];
	// change byte order
	double azi = 0;
	azi = (unsigned char) dataset[offset + 2];
	azi += ((unsigned char) dataset[offset + 3]) << 8;
	azi /= 100.0;
	return azi;
}

double VdDataset::getTime() {
	/*
	 gets timestamp of dataset
	 :return: timestamp of dataset
	 :rtype: int
	 */

	double time = ((unsigned char) dataset[1200])
			+ (((unsigned char) dataset[1201]) << 8)
			+ (((unsigned char) dataset[1202]) << 16)
			+ (((unsigned char) dataset[1203]) << 24);
	return time;
}

bool VdDataset::isDualReturn() {
	/*
	 checks whether dual return is activated
	 :return: dual return active?
	 :rtype: bool
	 */

	int mode = (unsigned char) dataset[1204];
	//cout << mode << endl;
	if (mode == 57) {
		//cout << "dr" << endl;
		return true;
	}
	return false;
}

void VdDataset::getAzimuths(double azimuths[], double rotation[]) {
	/*
	 get all azimuths and rotation angles from dataset
	 :return: azimuths and rotation angles
	 :rtype: list, list
	 */

	// read existing azimuth values
	for (int j = 0; j < 24; j += 2) {
		double a = this->getAzimuth((int) j / 2);
		azimuths[j] = a;
	}

	// rotation angle
	double d = 0;
	// DualReturn active?
	if (this->isDualReturn()) {
		for (int j = 0; j < 19; j += 4) {
			double d2 = azimuths[j + 4] - azimuths[j];
			if (d2 < 0) {
				d2 += 360.0;
			}
			d = d2 / 2.0;
			double a = azimuths[j] + d;
			azimuths[j + 1] = a;
			azimuths[j + 3] = a;
			rotation[(int) j / 2] = d;
			rotation[(int) j / 2 + 1] = d;
		}
		rotation[10] = d;
		azimuths[21] = azimuths[20] + d;
	}
	// Strongest / Last-Return
	else {
		for (int j = 0; j < 22; j += 2) {
			double d2 = azimuths[j + 2] - azimuths[j];
			if (d2 < 0) {
				d2 += 360.0;
			}
			d = d2 / 2.0;
			double a = azimuths[j] + d;
			azimuths[j + 1] = a;
			rotation[(int) j / 2] = d;
		}
	}
	// last rotation angle from angle before
	rotation[11] = d;
	azimuths[23] = azimuths[22] + d;

	// >360 -> -360
	for (int j = 0; j < 24; j++) {
		while (azimuths[j] > 360.0) {
			azimuths[j] -= 360.0;
		}
	}

}

void VdDataset::convertData() {
	/* converts binary data to objects */
	double t_between_laser = 2.304;
	double t_recharge = 20.736;
	double part_rotation = 0.041666666666666664;

	// create empty lists
	double azimuth[24];
	double rotation[12];
	this->getAzimuths(azimuth, rotation);

	bool dual_return = this->isDualReturn();

// timestamp from dataset
	double time = this->getTime();
	double times[12] = { };
	double t_2repeat = 2 * tRepeat;
	if (dual_return) {
		for (int i = 0; i < 12; i += 2) {
			times[i] = time;
			times[i + 1] = time;
			time += t_2repeat;
		}
	} else {
		for (int i = 0; i < 12; i++) {
			times[i] = time;
			time += t_2repeat;
		}
	}
	double azi_block, a;

	// data package has 12 blocks with 32 measurements
	for (int i = 0; i < 12; i++) {
		int offset = this->offsets[i];
		time = times[i];
		for (int j = 0; j < 2; j++) {
			azi_block = azimuth[(int) i * 2 + j];
			for (int k = 0; k < 16; k++) {
				// get distance
				double dist = ((unsigned char) this->dataset[4 + offset])
						+ (((unsigned char) this->dataset[5 + offset]) << 8);
				if (dist > 0.0) {
					dist /= 500.0;

					int reflection = (unsigned char) this->dataset[offset + 6];

					// interpolate azimuth
					a = azi_block + rotation[i] * k * part_rotation;
					// print(a)

					// create point
					VdPoint p(time, a, verticalAngle[k], dist, reflection);
					data.push_back(p);
				}
				time += t_between_laser;

				// offset for next loop
				offset += 3;
			}
			time += t_recharge - t_between_laser;
		}
	}
}
