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
    
class ShotErrorMail(ShotError):
    pass

class ShotErrorInvalidPage(ShotError):
    def __init__(self, page = None):
        
        if page:
            s = ' (%s)' % page
        else:
            s = ''
            
        self.msg = 'Invalid page reference%s!' %s
        
