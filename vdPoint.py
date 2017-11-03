#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Florian Timm
@version: 2017.10.26
'''

class VdPoint(object):
    ''' Stellt eine Messung da '''
    
    def __init__(self, zeit, azimut, vertikal, distanz, reflexion):
        
        self.zeit = zeit
        self.azimut = azimut
        self.vertikal = vertikal
        self.reflexion = reflexion
        self.distanz = distanz