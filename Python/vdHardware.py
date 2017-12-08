#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.20
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

        self.__taster_start = 5  # start
        self.__taster_stop = 13 # stop
        self.__taster_shutdown = 26  # shutdown

        # led-pins:
        # 0: receiving
        # 1: queue
        # 2: recording
        self.__led = [2,4,17]
        self.__receiving = False
        self.__queue = False
        self.__recording = False

        self.__master = master

        # activate input pins
        # recording start
        GPIO.setup(self.__taster_start, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # recording stop
        GPIO.setup(self.__taster_stop, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # shutdown
        GPIO.setup(self.__taster_shutdown, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # activate outputs
        for l in self.__led:
            GPIO.setup(l, GPIO.OUT)  # GPS-Fix
            GPIO.output(l, GPIO.LOW)

        self.__go_on = True

    def run(self):
        """ run thread and start hardware control """
        GPIO.add_event_detect(
            self.__taster_start,
            GPIO.FALLING,
            self.__start_pressed)
        GPIO.add_event_detect(
            self.__taster_stop,
            GPIO.FALLING,
            self.__stop_pressed)
        GPIO.add_event_detect(
            self.__taster_shutdown,
            GPIO.FALLING,
            self.__shutdown_pressed)

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

    def __start_pressed(self, channel):
        """ raised when button 1 is pressed """
        time.sleep(0.1)  # contact bounce

        pressed = True
        # > 2 seconds
        for i in range (4):
            if GPIO.input(self.__taster_start) == 0:
                pressed = False
            time.sleep(0.5)

        if pressed:
            # no rising edge = pressed
            self.__master.start_recording()

    def __stop_pressed(self, channel):
        """ raised when button 1 is pressed """
        time.sleep(0.1)  # contact bounce

        if GPIO.input(self.__taster_stop) == 1:
            # no rising edge = pressed
            self.__master.stop_recording()

    def __shutdown_pressed(self, channel):
        """ raised when button 1 is pressed """
        time.sleep(2)  # contact bounce

        if GPIO.input(self.__taster_shutdown) == 1:
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
