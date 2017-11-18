#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.18
"""

import configparser
import multiprocessing
import os
import signal
import sys
import time
from datetime import datetime
from multiprocessing import Queue, Manager
from threading import Thread
from flask import Flask
from vdBuffer import VdBuffer
from vdTransformer import VdTransformer
from vdGNSSTime import VdGNSSTime


class VdAutoStart(object):

    """ main script for automatic start """

    def __init__(self, web_interface):
        """
        Constructor
        :param web_interface: Thread with Flask web interface
        :type web_interface: Thread
        """
        self._vd_hardware = None
        print("Data Interface for VLP-16\n")

        # load config file
        self._conf = configparser.ConfigParser()
        self._conf.read("config.ini")

        # variables for child processes
        self._pBuffer = None
        self._pTransformer = None

        # pipes for child processes
        manager = Manager()
        self._gnss_status = "(unknown)"
        # self._gnssReady = manager.Value('gnssReady',False)
        self._go_on_buffer = manager.Value('_go_on_buffer', False)
        self._go_on_transform = manager.Value('_go_on_transform', False)
        self._scanner_status = manager.Value('_scanner_status', "(unknown)")
        self._dataset_cnt = manager.Value('_dataset_cnt', 0)
        self._date = manager.Value('_date', None)

        # queue for transformer
        self._queue = Queue()

        # attribute for web interface
        self._web_interface = web_interface

        # check root
        try:
            os.rename('/etc/foo', '/etc/bar')
            self._admin = True
        except IOError:
            self._admin = False

        # check raspberry pi
        try:
            import RPi.GPIO
            self._raspberry = True
        except ModuleNotFoundError:
            self._raspberry = False

        self._gnss = None

    def run(self):
        """ start script """

        # handle SIGINT
        signal.signal(signal.SIGINT, self._signal_handler)

        # use hardware control on raspberry pi
        if self._raspberry:
            print("Raspberry Pi was detected")
            from vdHardware import VdHardware
            self._vd_hardware = VdHardware(self)
            self._vd_hardware.start()
        else:
            print("Raspberry Pi could not be detected")
            print("Hardware control deactivated")

        # set time by using gnss
        if self._conf.get("Funktionen", "GNSSZeitVerwenden"):
            self._gnss = VdGNSSTime(self)
            self._gnss.start()

    def start_transformer(self):
        """ Starts transformer processes"""
        print("Start transformer...")
        # number of transformer according number of processor cores
        if self._conf.get("Funktionen", "activateTransformer"):
            self._go_on_transform.value = True
            n = multiprocessing.cpu_count() - 1
            if n < 2:
                n = 1
            self._pTransformer = []
            for i in range(n):
                t = VdTransformer(i, self)
                t.start()
                self._pTransformer.append(t)

            print(str(n) + " transformer started!")

    def start_recording(self):
        """ Starts recording process"""
        if not (self._go_on_buffer.value and self._pBuffer.is_alive()):
            self._go_on_buffer.value = True
            print("Recording is starting...")
            self._scanner_status.value = "recording started"
            # buffering process
            self._pBuffer = VdBuffer(self)
            self._pBuffer.start()
        if self._pTransformer is None:
            self.start_transformer()

    def stop_recording(self):
        print("Recording is stopping... (10 seconds timeout before kill)")
        self._go_on_buffer.value = False
        self._date.value = None
        if self._pBuffer is not None:
            self._pBuffer.join(10)
            if self._pBuffer.is_alive():
                print("Could not stop process, it will be killed!")
                self._pBuffer.terminate()
            print("Recording terminated!")
        else:
            print("Recording was not started!")

    def stop_transformer(self):
        """ Stops transformer processes """
        print("Transformer is stopping... (10 seconds timeout before kill)")
        self._go_on_transform.value = False
        if self._pTransformer is not None:
            for pT in self._pTransformer:
                pT.join(15)
                if pT.is_alive():
                    print(
                        "Could not stop process, it will be killed!")
                    pT.terminate()
            print("Transformer terminated!")
        else:
            print("Transformer was not started!")

    def stop_web_interface(self):
        """ Stop web interface -- not implemented now"""
        # Todo
        # self._web_interface.exit()
        # print("Web interface stopped!")
        pass

    def stop_hardware_control(self):
        """ Stop hardware control """
        if self._vd_hardware is not None:
            self._vd_hardware.stop()
            self._vd_hardware.join(5)

    def stop_children(self):
        """ Stop child processes and threads """
        print("Script is stopping...")
        self.stop_recording()
        self.stop_transformer()
        self.stop_web_interface()
        self.stop_hardware_control()
        print("Child processes stopped")

    def end(self):
        """ Stop script complete """
        self.stop_children()
        sys.exit()

    def _signal_handler(self, sig_no, frame):
        """
        handles SIGINT-signal
        :param sig_no: signal number
        :type sig_no: int
        :param frame:execution frame
        :type frame: frame
        """
        del sig_no, frame
        print('Ctrl+C pressed!')
        self.stop_children()
        sys.exit()

    def shutdown(self):
        """ Shutdown Raspberry Pi """
        self.stop_children()
        os.system("sleep 5s; sudo shutdown -h now")
        print("Shutdown Raspberry...")
        sys.exit(0)

    def check_queue(self):
        """ Check, whether queue is filled """
        if self._queue.qsize() > 0:
            return True
        return False

    def check_recording(self):
        """ Check data recording by pBuffer """
        if self._pBuffer is not None and self._pBuffer.is_alive():
            return True
        return False

    def check_receiving(self):
        """ Check data receiving """
        x = self._dataset_cnt.value
        time.sleep(0.2)
        y = self._dataset_cnt.value
        if x - y > 0:
            return True
        return False

    # getter methods
    def get_conf(self):
        """
        Gets config file
        :return:
        :rtype:
        """
        return self._conf

    def get_gnss_status(self):
        """
        Gets GNSS status
        :return: GNSS status
        :rtype: Manager
        """
        return self._gnss_status

    def get_go_on_buffer(self):
        """
        Should Buffer buffer data?
        :return: go on buffering
        :rtype: Manager
        """
        return self._go_on_buffer

    def get_go_on_transform(self):
        """
        Should Transformer transform data?
        :return: go on transforming
        :rtype: Manager
        """
        return self._go_on_transform

    def get_scanner_status(self):
        """
        Gets scanner status
        :return:
        :rtype: Manager
        """
        return self._scanner_status

    def get_dataset_cnt(self):
        """
        Gets number of buffered datasets
        :return: number of buffered datasets
        :rtype: Manager
        """
        return self._dataset_cnt

    def get_date(self):
        """
        Gets recording start time
        :return: timestamp starting recording
        :rtype: Manager
        """
        return self._date

    def is_root(self):
        """
        Root?
        :return: root?
        :rtype: bool
        """
        return self._admin

    def get_queue(self):
        """
        Gets transformer queue
        :return: transformer queue
        :rtype: Queue
        """
        return self._queue

    # setter-methods
    def set_date(self, date):
        """
        Sets recording start time
        :param date: timestamp starting recording
        :type date: datetime
        """
        self._date = date

    def set_gnss_status(self, gnss_status):
        """
        Sets GNSS status
        :param gnss_status: gnss status
        :type gnss_status: str
        """
        self._gnss_status = gnss_status


# Websteuerung
app = Flask(__name__)


@app.route("/")
def _web_index():
    runtime = "(inactive)"
    pps = "(inactive)"
    if ms.get_date().value is not None:
        timediff = datetime.now() - ms.get_date().value
        td_sec = timediff.seconds + (int(timediff.microseconds / 1000) / 1000.)
        sec = td_sec % 60
        minu = int((td_sec // 60) % 60)
        h = int(td_sec // 3600)

        runtime = '{:02d}:{:02d}:{:06.3f}'.format(h, minu, sec)

        pps = '{:.0f}'.format(ms.get_dataset_cnt().value / td_sec)

    elif ms.get_go_on_buffer().value:
        runtime = "(no data)"

    ausgabe = """<html>
    <head>
        <title>VLP16-Data-Interface</title>
        <meta name="viewport" content="width=device-width; initial-scale=1.0;" />
        <link href="/style.css" rel="stylesheet">
        <meta http-equiv="refresh" content="5; URL=/">
    </head>
    <body>
    <content>
        <h2>VLP16-Data-Interface</h3>
        <table style="">
            <tr><td id="spalte1">GNSS-status:</td><td>""" + ms.get_gnss_status() + """</td></tr>
            <tr><td>Scanner:</td><td>""" + ms.get_scanner_status().value + """</td></tr>
            <tr><td>Datasets</td>
                <td>""" + str(ms.get_dataset_cnt().value) + """</td></tr>
            <tr><td>Queue:</td>
                <td>""" + str(ms.get_queue().qsize()) + """</td></tr>
            <tr><td>Recording time:</td>
                <td>""" + runtime + """</td>
            </tr>
            <tr><td>Points/seconds:</td>
                <td>""" + pps + """</td>
            </tr>
        </table><br />
                """
    if ms.check_recording():
        ausgabe += """<a href="/stoppen" id="stoppen">
            Stop recording</a><br />"""
    else:
        ausgabe += """<a href="/starten" id="starten">
            Start recording</a><br />"""
    ausgabe += """
        <a href="/beenden" id="beenden">Terminate script<br />
        (control by SSH available only)</a></td></tr><br />
        <a href="/shutdown" id="shutdown">Shutdown Raspberry Pi</a>
    </content>
    </body>
    </html>"""

    return ausgabe


@app.route("/style.css")
def _css_style():
    return """
    body, html, content {
        text-align: center;
    }

    content {
        max-width: 15cm;
        display: block;
        margin: auto;
    }

    table {
        border-collapse: collapse;
        width: 90%;
        margin: auto;
    }

    td {
        border: 1px solid black;
        padding: 1px 2px;
    }

    td#spalte1 {
        width: 30%;
    }

    a {
        display: block;
        width: 90%;
        padding: 0.5em 0;
        text-align: center;
        margin: auto;
        color: #fff;
    }

    a#stoppen {
        background-color: #e90;
    }

    a#shutdown {
        background-color: #b00;
    }

    a#starten {
        background-color: #1a1;
    }

    a#beenden {
        background-color: #f44;
    }
    """


@app.route("/shutdown")
def _web_shutdown():
    ms.shutdown()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Wird in 10 Sekunden heruntergefahren..."""


@app.route("/beenden")
def _web_exit():
    ms.end()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Terminating..."""


@app.route("/stoppen")
def _web_stop():
    ms.stop_recording()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Recording is stopping..."""


@app.route("/starten")
def _web_start():
    ms.start_recording()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Recording is starting..."""


def _start_web():
    print("Webserver is starting...")
    app.run('0.0.0.0', 8080)


if __name__ == '__main__':
    w = Thread(target=_start_web)
    ms = VdAutoStart(w)
    w.start()
    ms.run()
