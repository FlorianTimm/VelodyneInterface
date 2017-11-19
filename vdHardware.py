#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.19
"""

import RPi.GPIO as GPIO
import time
from threading import Thread
import threading


class VdHardware(Thread):

    """ controls hardware control, extends Thread """

    def __init__(self, master):
        """
        Constructor
        :param master: instance of VdAutoStart
        :type master: VdAutoStart
        """
        Thread.__init__(self)

        GPIO.setmode(GPIO.BCM)

        self.__taster1 = 18  # start / stop
        self.__taster2 = 25  # shutdown

        # led-pins:
        # 0: receiving
        # 1: queue
        # 2: recording
        self.__led = [10, 9, 11]
        self.__receiving = False
        self.__queue = False
        self.__recording = False

        self.__master = master

        # activate input pins
        # recording start/stop
        GPIO.setup(self.__taster1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # shutdown
        GPIO.setup(self.__taster2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # activate outputs
        for l in self.__led:
            GPIO.setup(l, GPIO.OUT)  # GPS-Fix
            GPIO.output(l, GPIO.LOW)

        self.__go_on = True

    def run(self):
        """ run thread and start hardware control """
        GPIO.add_event_detect(
            self.__taster1,
            GPIO.FALLING,
            self.__button1_pressed)
        GPIO.add_event_detect(
            self.__taster2,
            GPIO.FALLING,
            self.__button1_pressed)

        self.__timer_check_leds()

    def __timer_check_leds(self):
        """ checks LEDs every second """
        self.__check_leds()
        if self.__go_on:
            t = threading.Timer(1, self.__timer_check_leds)
            t.start()

    def __check_leds(self):
        """ check LEDs """
        self.__set_recording(self.__master.check_recording())
        self.__set_receiving(self.__master.check_receiving())
        self.__set_queue(self.__master.check_queue())

    def __button1_pressed(self):
        """ raised when button 1 is pressed """
        time.sleep(0.1)  # contact bounce

        # > 2 seconds
        wait = GPIO.wait_for_edge(self.__taster1, GPIO.RISING, timeout=1900)

        if wait is None:
            # no rising edge = pressed
            if self.__master.go_on_buffer.value:
                self.__master.stop_recording()
            else:
                self.__master.start_recording()

    def __button2_pressed(self):
        """ raised when button 1 is pressed """
        time.sleep(0.1)  # contact bounce

        # > 2 seconds
        wait = GPIO.wait_for_edge(self.__taster2, GPIO.RISING, timeout=1900)

        if wait is None:
            # no rising edge = pressed
            self.__master.shutdown()

    def __switch_led(self, led, yesno):
        """
        switch led
        :param led: pin of led
        :type led: int
        :param yesno: True = on
        :type yesno: bool
        """
        if yesno:
            GPIO.output(self.__led[led], GPIO.HIGH)
        else:
            GPIO.output(self.__led[led], GPIO.LOW)

    def __update_leds(self):
        """ switch all LEDs to right status """
        self.__switch_led(0, self.__receiving)
        self.__switch_led(1, self.__queue)
        self.__switch_led(2, self.__recording)

    def __set_receiving(self, yesno):
        """
        set receiving variable and led
        :param yesno: True = on
        :type yesno: bool
        """
        if self.__receiving != yesno:
            self.__receiving = yesno
            self.__update_leds()

    def __set_queue(self, yesno):
        """
        set queue variable and led
        :param yesno: True = on
        :type yesno: bool
        """
        if self.__queue != yesno:
            self.__queue = yesno
            self.__update_leds()

    def __set_recording(self, yesno):
        """
        set recording variable and led
        :param yesno: True = on
        :type yesno: bool
        """
        if self.__recording != yesno:
            self.__recording = yesno
            self.__update_leds()

    def stop(self):
        """ stops thread """
        self.__go_on = False
        GPIO.cleanup()
