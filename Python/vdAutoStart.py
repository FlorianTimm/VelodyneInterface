#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.20
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
        self.__vd_hardware = None
        print("Data Interface for VLP-16\n")

        # load config file
        self.__conf = configparser.ConfigParser()
        self.__conf.read("config.ini")

        # variables for child processes
        self.__pBuffer = None
        self.__pTransformer = None

        # pipes for child processes
        manager = Manager()
        self.__gnss_status = "(unknown)"
        # self.__gnssReady = manager.Value('gnssReady',False)
        self.__go_on_buffer = manager.Value('_go_on_buffer', False)
        self.__go_on_transform = manager.Value('_go_on_transform', False)
        self.__scanner_status = manager.Value('__scanner_status', "(unknown)")
        self.__dataset_cnt = manager.Value('__dataset_cnt', 0)
        self.__date = manager.Value('__date', None)

        # queue for transformer
        self.__queue = Queue()

        # attribute for web interface
        self.__web_interface = web_interface

        # check admin
        try:
            os.rename('/etc/foo', '/etc/bar')
            self.__admin = True
        except IOError:
            self.__admin = False

        # check raspberry pi
        try:
            import RPi.GPIO
            self.__raspberry = True
        except ModuleNotFoundError:
            self.__raspberry = False

        self.__gnss = None

    def run(self):
        """ start script """

        # handle SIGINT
        signal.signal(signal.SIGINT, self.__signal_handler)

        # use hardware control on raspberry pi
        if self.__raspberry:
            print("Raspberry Pi was detected")
            from vdHardware import VdHardware
            self.__vd_hardware = VdHardware(self)
            self.__vd_hardware.start()
        else:
            print("Raspberry Pi could not be detected")
            print("Hardware control deactivated")

        # set time by using gnss
        if self.__conf.get("functions", "use_gnss_time") == "True":
            self.__gnss = VdGNSSTime(self)
            self.__gnss.start()

    def start_transformer(self):
        """ Starts transformer processes"""
        print("Start transformer...")
        # number of transformer according number of processor cores
        if self.__conf.get("functions", "activateTransformer") == "True":
            self.__go_on_transform.value = True
            n = multiprocessing.cpu_count() - 1
            if n < 2:
                n = 1
            self.__pTransformer = []
            for i in range(n):
                t = VdTransformer(i, self)
                t.start()
                self.__pTransformer.append(t)

            print(str(n) + " transformer started!")

    def start_recording(self):
        """ Starts recording process"""
        if not (self.__go_on_buffer.value and self.__pBuffer.is_alive()):
            self.__go_on_buffer.value = True
            print("Recording is starting...")
            self.__scanner_status.value = "recording started"
            # buffering process
            self.__pBuffer = VdBuffer(self)
            self.__pBuffer.start()
        if self.__pTransformer is None:
            self.start_transformer()

    def stop_recording(self):
        """ stops buffering data """
        print("Recording is stopping... (10 seconds timeout before kill)")
        self.__go_on_buffer.value = False
        self.__date.value = None
        if self.__pBuffer is not None:
            self.__pBuffer.join(10)
            if self.__pBuffer.is_alive():
                print("Could not stop process, it will be killed!")
                self.__pBuffer.terminate()
            print("Recording terminated!")
        else:
            print("Recording was not started!")

    def stop_transformer(self):
        """ Stops transformer processes """
        print("Transformer is stopping... (10 seconds timeout before kill)")
        self.__go_on_transform.value = False
        if self.__pTransformer is not None:
            for pT in self.__pTransformer:
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
        # self.__web_interface.exit()
        # print("Web interface stopped!")
        pass

    def stop_hardware_control(self):
        """ Stop hardware control """
        if self.__vd_hardware is not None:
            self.__vd_hardware.stop()
            self.__vd_hardware.join(5)

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

    def __signal_handler(self, sig_no, frame):
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
        if self.__queue.qsize() > 0:
            return True
        return False

    def check_recording(self):
        """ Check data recording by pBuffer """
        if self.__pBuffer is not None and self.__pBuffer.is_alive():
            return True
        return False

    def check_receiving(self):
        """ Check data receiving """
        x = self.__dataset_cnt.value
        time.sleep(0.2)
        y = self.__dataset_cnt.value
        if x - y > 0:
            return True
        return False

    # getter/setter methods
    def __get_conf(self):
        """
        Gets config file
        :return: config file
        :rtype: configparser.ConfigParser
        """
        return self.__conf
    conf = property(__get_conf)

    def __get_gnss_status(self):
        """
        Gets GNSS status
        :return: GNSS status
        :rtype: Manager
        """
        return self.__gnss_status

    def __set_gnss_status(self, gnss_status):
        """
        Sets GNSS status
        :param gnss_status: gnss status
        :type gnss_status: str
        """
        self.__gnss_status = gnss_status
    gnss_status = property(__get_gnss_status, __set_gnss_status)

    def __get_go_on_buffer(self):
        """
        Should Buffer buffer data?
        :return: go on buffering
        :rtype: Manager
        """
        return self.__go_on_buffer
    go_on_buffer = property(__get_go_on_buffer)

    def __get_go_on_transform(self):
        """
        Should Transformer transform data?
        :return: go on transforming
        :rtype: Manager
        """
        return self.__go_on_transform
    go_on_transform = property(__get_go_on_transform)

    def __get_scanner_status(self):
        """
        Gets scanner status
        :return:
        :rtype: Manager
        """
        return self.__scanner_status
    scanner_status = property(__get_scanner_status)

    def __get_dataset_cnt(self):
        """
        Gets number of buffered datasets
        :return: number of buffered datasets
        :rtype: Manager
        """
        return self.__dataset_cnt
    dataset_cnt = property(__get_dataset_cnt)

    def __get_date(self):
        """
        Gets recording start time
        :return: timestamp starting recording
        :rtype: Manager
        """
        return self.__date

    def __set_date(self, date):
        """
        Sets recording start time
        :param date: timestamp starting recording
        :type date: datetime
        """
        self.__date = date
    #: recording start time
    date = property(__get_date, __set_date)

    def __is_admin(self):
        """
        Admin?
        :return: Admin?
        :rtype: bool
        """
        return self.__admin
    admin = property(__is_admin)

    def __get_queue(self):
        """
        Gets transformer queue
        :return: transformer queue
        :rtype: Queue
        """
        return self.__queue
    queue = property(__get_queue)


# web control
app = Flask(__name__)


@app.route("/")
def web_index():
    """ index page of web control """
    runtime = "(inactive)"
    pps = "(inactive)"
    if ms.date.value is not None:
        time_diff = datetime.now() - ms.date.value
        td_sec = time_diff.seconds + \
            (int(time_diff.microseconds / 1000) / 1000.)
        seconds = td_sec % 60
        minutes = int((td_sec // 60) % 60)
        hours = int(td_sec // 3600)

        runtime = '{:02d}:{:02d}:{:06.3f}'.format(hours, minutes, seconds)

        pps = '{:.0f}'.format(ms.dataset_cnt.value / td_sec)

    elif ms.go_on_buffer.value:
        runtime = "(no data)"

    output = """<html>
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
            <tr><td id="column1">GNSS-status:</td><td>""" + ms.gnss_status + """</td></tr>
            <tr><td>Scanner:</td><td>""" + ms.scanner_status.value + """</td></tr>
            <tr><td>Datasets</td>
                <td>""" + str(ms.dataset_cnt.value) + """</td></tr>
            <tr><td>Queue:</td>
                <td>""" + str(ms.queue.qsize()) + """</td></tr>
            <tr><td>Recording time:</td>
                <td>""" + runtime + """</td>
            </tr>
            <tr><td>Points/seconds:</td>
                <td>""" + pps + """</td>
            </tr>
        </table><br />
                """
    if ms.check_recording():
        output += """<a href="/stop" id="stop">
            Stop recording</a><br />"""
    else:
        output += """<a href="/start" id="start">
            Start recording</a><br />"""
    output += """
        <a href="/exit" id="exit">Terminate script<br />
        (control by SSH available only)</a></td></tr><br />
        <a href="/shutdown" id="shutdown">Shutdown Raspberry Pi</a>
    </content>
    </body>
    </html>"""

    return output


@app.route("/style.css")
def css_style():
    """ css file of web control """
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

    td#column1 {
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

    a#stop {
        background-color: #e90;
    }

    a#shutdown {
        background-color: #b00;
    }

    a#start {
        background-color: #1a1;
    }

    a#exit {
        background-color: #f44;
    }
    """


@app.route("/shutdown")
def web_shutdown():
    """ web control: shutdown """
    ms.shutdown()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Shutdown..."""


@app.route("/exit")
def web_exit():
    """ web control: exit """
    ms.end()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Terminating..."""


@app.route("/stop")
def web_stop():
    """ web control: stop buffering """
    ms.stop_recording()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Recording is stopping..."""


@app.route("/start")
def web_start():
    """ web control: start buffering """
    ms.start_recording()
    return """
    <meta http-equiv="refresh" content="3; URL=/">
    Recording is starting..."""


def start_web():
    """ start web control """
    print("Web server is starting...")
    app.run('0.0.0.0', 8080)


if __name__ == '__main__':
    w = Thread(target=start_web)
    ms = VdAutoStart(w)
    w.start()
    ms.run()
