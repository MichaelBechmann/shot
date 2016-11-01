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
    '''
    This error shall be raised some requested page does not exist or if page arguments are invalid.
    '''
    def __init__(self, page = None):
        
        if page:
            s = ' (%s)' % page
        else:
            s = ''
            
        self.msg = 'Invalid page reference%s!' %s
        
        
class ShotErrorRobot(ShotError):
    '''
    This error shall be raised if robots are detected filling the forms.
    '''
    def __init__(self, comment = None):
        
        if comment:
            s = ' (%s)' % comment
        else:
            s = ''
            
        self.msg = 'A robot has been detected filling a form%s!' % s