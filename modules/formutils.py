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

def addMailEnabledElement(form):
    mail_enabled_element = TR(TD(), TD(
                DIV( DIV('Einladungen zu künftigen Märkten per E-Mail', _class = 'agree_header'),
                TABLE(TR(INPUT(_name='mail_enabled', _type = 'radio', _value = 'yes'), config.mail_enabled_options['yes']),
                      TR(INPUT(_name='mail_enabled', _type = 'radio', _value = 'no'),  config.mail_enabled_options['no'])
                      ),
                _class = 'agree_widget'
                )), TD())
    form[0].insert(-1, mail_enabled_element)

def addDataAgreedElement(form, type):
    data_agreed_element = TR(TD(), TD(
                DIV(DIV('Einwilligung zur Datenverarbeitung', _class = 'agree_header'),
                    TABLE(TR(INPUT(_name='data_use_agreed', _value='on', _type='checkbox'), config.data_use_agreed_option[type])
                    ), _class = 'agree_widget'
                    ), _colspan="2"))
    form[0].insert(-1, data_agreed_element)

def getPersonDataTable(vars, type):
    '''
    This function generates a standard table with person data for the confirmation pages.
    Note: Translation doesn't work. Something is wrong with the includes ...
    '''

    # construct display of data to be confirmed
    data_items = [
                   TR(TD('Ihr Name:', _class = 'label'), vars['forename'] + ' ' + vars['name']),
                   TR(TD('Ihre Adresse:', _class = 'label'), vars['zip_code'] + ' ' + vars['place'] + ', ' + vars['street'] + ' ' + vars['house_number'] ),
                   TR(TD('Ihre Telefonnummer:', _class = 'label'), vars['telephone']),
                   TR(TD('Ihre E-Mail-Adresse:', _class = 'label'), vars['email']),

                ]
    if 'mail_enabled' in vars:
        data_items.extend([
                   TR(TD('Einladungen:', _class = 'label'), config.mail_enabled_options[vars['mail_enabled']])
            ])

    if 'data_use_agreed' in vars:
        data_items.extend([
                   TR(TD('Persönliche Daten:'), TD(config.data_use_agreed_option[type]))
            ])

    return  TABLE(*data_items, _class = config.cssclass.tblconfirmdata)

def getAppRequestDataTable(vars):
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

def getAppRequestDataTableTeamInfo(vars):
    '''
    This function generates a table of the most important information on an appropriation request for the team info email.
    '''
    data_items = [
                   TR(TD('Projektbezeichung:', _class = 'label'),         vars['project']),
                   TR(TD('Organisation:', _class = 'label'),              vars['organization']),
                ]

    return TABLE(*data_items, _class = config.cssclass.tblconfirmdata)

def TableCtrlHead(tablename,
                  crud_function = 'crud',
                  addlinktext = 'Click here to add new entry',
                  sorttext = 'Click column head to sort'):
    '''
    This function returns a DIV container with the control elements for typical SQL tables.
    '''
    elem = []
    if addlinktext:
        addlink = A(addlinktext, _href=URL(crud_function, args = [tablename, 'add']))
        elem.extend([SPAN('+', _class = 'symbol'), SPAN(addlink, _class = 'text')])
    if sorttext:
        elem.extend([SPAN(XML('&darr;'), _class = 'symbol'), SPAN(sorttext, _class = 'text')])

    return(DIV(*elem, _class = 'table_ctrl'))


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


class Progress():
    '''
    This class provides methods to generate progress bars for all multi-page forms.
    '''
    def __init__(self, bardata, current_step):
        self.label        = bardata['label']
        self.steplist     = bardata['steps']
        self.current_step = current_step
        self.bar          = None

    def getProgressBar(self):
        if not self.bar:
            elements = []
            step = 0
            for element in self.steplist:
                step += 1
                if step < self.current_step:
                    c = config.cssclass.progressdone
                elif step == self.current_step:
                    c = config.cssclass.progresscurrent
                else:
                    c = config.cssclass.progressmissing
                elements.append(DIV(SPAN('%d. %s' % (step, element)), _class = c))

            self.bar = DIV(DIV(SPAN(self.label), _class = config.cssclass.progresslabel),
                           DIV(*elements, _class = config.cssclass.progresssteps),
                           _class = config.cssclass.progressbar)

        return self.bar
