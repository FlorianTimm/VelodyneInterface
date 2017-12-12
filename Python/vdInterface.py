#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.19
"""

import socket
import sys


class VdInterface(object):

    """ interface to velodyne scanner """

    @staticmethod
    def get_data_stream(conf):
        """
        Creates socket to scanner data stream
        :param conf: configuration file
        :type conf: configparser.ConfigParser
        :return: socket to scanner
        :rtype: socket.socket
        """
        return VdInterface.get_stream(conf.get("network", "UDP_IP"),
                                      int(conf.get("network", "UDP_PORT_DATA")))

    @staticmethod
    def get_gnss_stream(conf):
        """
        Creates socket to scanner gnss stream
        :param conf: configuration file
        :type conf: configparser.ConfigParser
        :return: socket to scanner
        :rtype: socket.socket
        """
        return VdInterface.get_stream(conf.get("network", "UDP_IP"),
                                      int(conf.get("network", "UDP_PORT_GNSS")))

    @staticmethod
    def get_stream(ip, port):
        """
        Creates socket to scanner stream
        :param ip: ip address of scanner
        :type ip: str
        :param port: port of scanner
        :type port: int
        :return: socket to scanner
        :rtype: socket.socket
        """

        # Create Datagram Socket (UDP)
        try:
            # IPv4 UDP
            sock = socket.socket(type=socket.SOCK_DGRAM)
            print('Socket created!')
        except socket.error:
            print('Could not create socket!')
            sys.exit()

        # Sockets Options
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Allows broadcast UDP packets to be sent and received.

        # Bind socket to local host and port
        try:
            sock.bind((ip, port))
        except socket.error:
            print('Bind failed.')

        print('Socket connected!')

        # now keep talking with the client
        print('Listening on: ' + ip + ':' + str(port))

        return sock
