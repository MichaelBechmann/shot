# -*- coding: utf-8 -*-
'''
creation: bechmann, Aug 21, 2013

This module contains miscellaneous utility functions for the processing of forms
'''

from shotconfig import * 
import re
from gluon.html import *


def getActNumberRatio(a, t):
    '''
    This function returns a dictionary with the following fields:
    'ratio':    fraction of actual number from target number in %
    '_class':    css class for coloring the fraction
    '''
    if t != 0:
        r = round(1.0*a/t*100)
    else:
        r = 100

    if r < 50:
        c = config.cssclass.actnumberlow
    elif r < 90:
        c = config.cssclass.actnumbermed
    else:
        c = config.cssclass.actnumberhigh
        
    return dict(ratio = r, _class = c)


def regularizeName(s):
    '''
    This function capitalizes strings like person names  in forms.
    Examples: testing/NameRegularization.py
    '''
    
    # remove leading and trailing spaces
    reg = s.lstrip().rstrip()
    
    for sep in (' ', '-'):
        reg = re.sub('\s*' + sep + '\s*', sep, reg)  
          
    exceptions = ('von' , 'der', 'van', 'de', 'du', 'e.V.')

    aux = []
    for part in reg.split(' '):
        aux.append('-'.join([x in exceptions and x or x.decode('utf-8').capitalize().encode('utf-8') for x in part.split('-')]))
    reg = ' '.join(aux)
    
    return reg

def regularizeFormInputPersonorm(form):
    '''
    This function brings the user input to standard.
    '''
    for field in ('forename', 'name', 'street', 'place'):
        form.vars[field] = regularizeName(form.vars[field])

    # check zip code
    s = form.vars['zip_code']
    s = s.replace(' ', '')
    if re.search('\D', s):
        form.errors.zip_code = 'Bitte geben Sie eine gültige Postleitzahl an.'
    form.vars['zip_code'] = s


def getPersonDataTable(vars):
    '''
    This function generates a standard table with person data for the confirmation pages.
    Note: Translation doesn't work. Something is wrong with the includes ...
    '''
    
    # construct display of data to be confirmed
    data_items = [
                   TR(TD('Ihr Name:', _class = 'label'), vars['forename'] + ' ' + vars['name']),
                   TR(TD('Ihre Adresse:', _class = 'label'), vars['zip_code'] + ' ' + vars['place'] + ', ' + vars['street'] + ' ' + vars['house_number'] ),
                   TR(TD('Ihre Telefonnummer:', _class = 'label'), vars['telephone']),
                   TR(TD('Ihre E-Mail-Adresse:', _class = 'label'), vars['email'])
                ]
        
    return  TABLE(*data_items, _class = config.cssclass.tblconfirmdata)

def getAppRequestDataTale(vars):
    data_items = [
                   TR(TD('Projektbezeichung:', _class = 'label'),         vars['project']),
                   TR(TD('Organisation:', _class = 'label'),              vars['organization']),
                   TR(TD(SPAN('Fördermittel:'),
                         DIV(SPAN('Sie beantragen Fördermittel in Höhe von '), STRONG(str(vars['amount_requested']) + ' EUR '), 
                             SPAN('bei Gesamtkosten des Projektes von %d EUR.' % vars['amount_total'])),
                            _colspan = 3, _class = 'fullrow')),
                   TR(TD(SPAN('Projektbeschreibung:'),
                         DIV(vars['description']), _colspan = 3, _class = 'fullrow'))
                ]
        
    return TABLE(*data_items, _class = config.cssclass.tblconfirmdata)



class TableUtils():
    '''
    This class provides simple helper methods for creating tables.
    '''
    evenoddclasses = ('even', 'odd')
    
    def __init__(self):
        self.reset()

    def get_class_evenodd(self):
        self.state_evenodd += 1
        return self.evenoddclasses[self.state_evenodd%2]

    def reset(self):
        self.state_evenodd = 0