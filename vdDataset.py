#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.11.16
'''

from vdPoint import VdPoint
import json


class VdDataset(object):

    """
    Klasse zur Repraesentation eines Datensatzes des VLP-16
    """

    def __init__(self, conf, dataset):
        """
        Konstruktor

        Parameters
        ----------
        dataset : bin
            Datensatz in binären Format
        masterSkript : VdAutoStart
            Objekt des Hauptskriptes
        """
        self._dataset = dataset
        self._conf = conf

        self._vertAngle = json.loads(self._conf.get("Geraet", "vertAngle"))
        self._offset = json.loads(self._conf.get("Geraet", "offset"))
        self._data = []

    def getAzimut(self, block):
        """
        Gibt den Horizontalrichtung eines Datenblockes zurück

        Parameters
        ----------
        block : int
            Nummer des Datenblockes

        Returns
        -------
        azi : float
            Horizontalrichtung des Datenblockes
        """
        offset = self._offset[block]
        # Horizontalrichtung zusammensetzen, Bytereihenfolge drehen
        azi = ord(self._dataset[offset + 2:offset + 3])
        azi += ord(self._dataset[offset + 3:offset + 4]) << 8
        azi /= 100.0
        return azi

    def getZeit(self):
        """
        Gibt den Timestamp des Datensatzes zurück

        Returns
        -------
        zeit : int
            Timestamp in Mikrosekunden
        """
        zeit = ord(self._dataset[1200:1201])
        zeit += ord(self._dataset[1201:1202]) << 8
        zeit += ord(self._dataset[1202:1203]) << 16
        zeit += ord(self._dataset[1203:1204]) << 24
        return zeit

    def isDualReturn(self):
        """
        Prueft, ob es sich um einen Datensatz mit zwei Echos
        pro Messung (DualReturn) handelt

        Returns
        -------
        x : boolean
            Datensatz mit zwei Echos pro Messung?
        """
        mode = ord(self._dataset[1204:1205])
        if (mode == 57):
            return True
        else:
            return False

    def getAzimuts(self):
        """
        Ruft alle Horizontalrichtungen und Drehwinkel
        pro Messung aus dem Datensatz ab

        Returns
        -------
        [azimuts, drehung] : list
            Mehrdimensionale Listen
        """

        # Leere Listen erzeugen
        azimuts = [None] * 24
        drehung = [None] * 12

        # Explizit uebermittelte Azimut-Werte einlesen
        for j in range(0, 24, 2):
            a = self.getAzimut(j // 2)
            azimuts[j] = a

        # Drehwinkelvariable initialisieren
        d = 0

        # DualReturn aktiv?
        if self.isDualReturn():
            for j in range(0, 19, 4):
                d2 = azimuts[j + 4] - azimuts[j]
                if d2 < 0:
                    d2 += 360.0
                d = d2 / 2.0
                a = azimuts[j] + d
                azimuts[j + 1] = a
                azimuts[j + 3] = a
                drehung[j // 2] = d
                drehung[j // 2 + 1] = d
            # Zweiten
            drehung[10] = d
            azimuts[21] = azimuts[20] + d

        # Strongest / Last-Return
        else:
            for j in range(0, 22, 2):
                d2 = azimuts[j + 2] - azimuts[j]
                if d2 < 0:
                    d2 += 360.0
                d = d2 / 2.0
                a = azimuts[j] + d
                azimuts[j + 1] = a
                drehung[j // 2] = d

        # letzter Drehwinkel wird immer vom vorherigen uebernommen,
        # letzte Horizontalrichtung ergibt sich aus diesem
        drehung[11] = d
        azimuts[23] = azimuts[22] + d

        # Auf Werte ueber 360 Grad pruefen
        for j in range(24):
            if azimuts[j] > 360.0:
                azimuts[j] -= 360.0

        return [azimuts, drehung]

    def convertData(self):
        """
        Wandelt die Datensätze vom Scanner in Objekte um
        """

        # Zeitstempel aus den Daten auslesen
        zeit = self.getZeit()

        # Richtung und Drehwinkel auslesen
        [azimut, drehung] = self.getAzimuts()

        # Datenpaket besteht aus 12 Bloecken aus jeweils 32 Messergebnissen
        for i in range(12):
            versatz = self._offset[i]
            for l in range(2):
                for k in range(16):

                    # Entfernung zusammensetzen
                    dist = ord(self._dataset[4 + versatz:5 + versatz])
                    dist += ord(self._dataset[5 + versatz:6 + versatz]) << 8
                    dist /= 500.0

                    # Reflektivitaet auslesen
                    refl = ord(self._dataset[6 + versatz:7 + versatz])

                    # Offset in Daten fuer den naechsten Durchlauf
                    versatz += 3

                    # Horizontalwinkel interpolieren
                    a = azimut[i + l]
                    a += drehung[i] * k * float(self._conf.get(
                        "Geraet", "antDrehung"))
                    # Punkt erzeugen und anhaengen
                    p = VdPoint(round(zeit, 1), a, self._vertAngle[k],
                                dist, refl)
                    self._data.append(p)
                    zeit += float(self._conf.get("Geraet", "tZwischenStrahl"))
                zeit += float(self._conf.get("Geraet", "tNachlade"))

    def getData(self):
        """
        Gibt die Daten als Liste zurück

        Returns
        -------
        self.data : list
            Liste mit VdPoint-Objekten
        """
        return self._data
