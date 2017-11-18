#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Florian Timm
@version: 2017.11.17
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

        self._taster1 = 18  # start / stop
        self._taster2 = 25  # shutdown

        # led-pins:
        # 0: receiving
        # 1: queue
        # 2: recording
        self._led = [10, 9, 11]
        self._receiving = False
        self._queue = False
        self._recording = False

        # Masterobjekt sichern
        self._master = master

        # Eingaenge aktivieren
        # Aufzeichnung starten/stoppen
        GPIO.setup(self._taster1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Herunterfahren
        GPIO.setup(self._taster2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Ausgaenge aktivieren und auf Low schalten
        for l in self._led:
            GPIO.setup(l, GPIO.OUT)  # GPS-Fix
            GPIO.output(l, GPIO.LOW)

        self._go_on = True

    def run(self):
        """ run thread and start hardware control """
        GPIO.add_event_detect(
            self._taster1,
            GPIO.FALLING,
            self._button1_pressed)
        GPIO.add_event_detect(
            self._taster2,
            GPIO.FALLING,
            self._button1_pressed)

        self._timer_check_leds()

    def _timer_check_leds(self):
        """ checks leds every second """
        self._check_leds()
        if self._go_on:
            t = threading.Timer(1, self._timer_check_leds)
            t.start()

    def _check_leds(self):
        """ check leds """
        self._set_recording(self._master.check_recording())
        self._set_receiving(self._master.check_receiving())
        self._set_queue(self._master.check_queue())

    def _button1_pressed(self):
        """ raised when button 1 is pressed """
        time.sleep(0.1)  # Prellen abwarten

        # mindestens 2 Sekunden druecken
        wait = GPIO.wait_for_edge(self._taster1, GPIO.RISING, timeout=1900)

        if wait is None:
            # keine steigende Kante = gehalten
            if self._master.get_go_on_buffer().value:
                self._master.stop_recording()
            else:
                self._master.start_recording()

    def _button2_pressed(self):
        """ raised when button 1 is pressed """
        time.sleep(0.1)  # Prellen abwarten

        # mindestens 2 Sekunden druecken
        wait = GPIO.wait_for_edge(self._taster2, GPIO.RISING, timeout=1900)

        if wait is None:
            # keine steigende Kante = gehalten
            self._master.shutdown()

    def _switch_led(self, led, yesno):
        """
        switch led
        :param led: pin of led
        :type led: int
        :param yesno: True = on
        :type yesno: bool
        """
        if yesno:
            GPIO.output(self._led[led], GPIO.HIGH)
        else:
            GPIO.output(self._led[led], GPIO.LOW)

    def _update_leds(self):
        """ switch all leds to right status """
        self._switch_led(0, self._receiving)
        self._switch_led(1, self._queue)
        self._switch_led(2, self._recording)

    def _set_receiving(self, yesno):
        """
        set receiving variable and led
        :param yesno: True = on
        :type yesno: bool
        """
        if self._receiving != yesno:
            self._receiving = yesno
            self._update_leds()

    def _set_queue(self, yesno):
        """
        set queue variable and led
        :param yesno: True = on
        :type yesno: bool
        """
        if self._queue != yesno:
            self._queue = yesno
            self._update_leds()

    def _set_recording(self, yesno):
        """
        set recording variable and led
        :param yesno: True = on
        :type yesno: bool
        """
        if self._recording != yesno:
            self._recording = yesno
            self._update_leds()

    def stop(self):
        """ stops thread """
        self._go_on = False
        GPIO.cleanup()
