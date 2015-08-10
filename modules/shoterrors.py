# -*- coding: utf-8 -*-
'''
creation: bechmann, Aug 18, 2013

This module defines special exception classes for the application shot.
'''

class ShotError(Exception):
    def __init__(self, msg = 'no error message'):
        self.msg = msg
        
    def __str__(self):
        return self.msg
    
class ShotMailError(ShotError):
    pass
