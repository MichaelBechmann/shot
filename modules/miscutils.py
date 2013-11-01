# -*- coding: utf-8 -*-
'''
creation: bechmann, Aug 21, 2013

This module contains miscellaneous utility functions
'''
import re

def regularizeName(s):
    '''
    This function capitalizes strings like person names  in forms.
    Examples: testing/NameRegularization.py
    '''
    
    # remove leading ans trailing spaces
    reg = s.lstrip().rstrip()
    
    for sep in (' ', '-'):
        reg = re.sub('\s*' + sep + '\s*', sep, reg)  
          
    exceptions = ('von' , 'der', 'van', 'de', 'du')

    aux = []
    for part in reg.split(' '):
        aux.append('-'.join([x in exceptions and x or x.decode('utf-8').capitalize().encode('utf-8') for x in part.split('-')]))
    reg = ' '.join(aux)
    
    return reg

class TableUtils():
    '''
    This class provides simple helper methods for creating tables.
    '''
    evenoddclasses = ('even', 'odd')
    
    def __init__(self):
        self.state_evenodd = 1
        
    def get_class_evenodd(self):
        self.state_evenodd += 1
        return self.evenoddclasses[self.state_evenodd%2]
