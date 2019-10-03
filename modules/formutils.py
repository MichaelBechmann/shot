# -*- coding: utf-8 -*-
'''
creation: bechmann, Aug 21, 2013

This module contains miscellaneous utility functions for the processing of forms
'''

from shotconfig import *
import re
from gluon.html import *




class FormButton():
    '''
    This class provides methods to generate values (strings) for form buttons including icons.
    '''
    def back(self, value = 'zurück', name = 'submit back'):
        return BUTTON(value, _type = 'submit', _name = name, _class = 'expanded button back')

    def next(self, value = 'weiter', name = 'submit next'):
        return BUTTON(value, _type = 'submit', _name = name,  _class = 'expanded button next')

    def send(self, value = 'senden', name = 'submit send'):
        return BUTTON(value, _type = 'submit', _name = name,  _class = 'expanded button send')


def generateFoundationForm(form, fields):
    '''
    This function is intended to be used as the formstyle argument in in the SQLFORM() constructor.
    The form is constructed according to https://foundation.zurb.com/sites/docs/forms.html.
    '''
    grid = DIV(_class = 'grid-container')

    for identifier, label, controls, help in fields:
        # Important: With web2py version 2.18.5 the additional DIV container in the line below is necessary for the validation of the form to work properly!
        # See gluon/sqlhtml.py line 1829 (parent.components = [widget]).
        grid.append(DIV(controls))

    return grid


def __foundation_widget_generic(field, value, HELPER, type = 'text', _class = None):
    identifier   = '%s_%s' % (field.tablename, field.name)
    label = LABEL(field.label + ':', _for = identifier, _class = 'text-left medium-middle')

    formelement = HELPER(_type        = type,
                         _id          = identifier,
                         _class       = '',
                         _name        = field.name,
                         _placeholder = field.comment,
                         requires     = field.requires)

    if (HELPER == TEXTAREA):
        formelement['_rows'] = 6
        if value:
            formelement.append(value)

    elif HELPER == SELECT:
        for (k, v) in field.requires.options():
            formelement.append(OPTION(v, _value = k))
    else:
        formelement['_value'] = value


    widget_class = 'grid-x grid-padding-x'
    if _class:
        widget_class = widget_class + ' ' + _class

    widget = DIV(DIV(label,       _class = 'medium-12 large-3 huge-2 cell'),
                 DIV(formelement, _class = 'medium-12 large-9 huge-10 cell'),
                 _class = widget_class)

    return widget

def FoundationWidgetString(field, value):
    return __foundation_widget_generic(field, value, INPUT)

def FoundationWidgetPassWord(field, value):
    return __foundation_widget_generic(field, value, INPUT, type = 'password')

def FoundationWidgetText(field, value):
    return __foundation_widget_generic(field, value, TEXTAREA)

def FoundationWidgetSelectAutosubmit(field, value):
    return __foundation_widget_generic(field, value, SELECT, type = 'select', _class = 'autosubmit')

def FoundationWidgetRadio(field, value, radio_options, default_value = None):
    if not value:
        value = default_value

    widget = FIELDSET(LEGEND(field.label), _class = 'fieldset no-bottom-padding')
    i = 0
    requires = field.requires
    for option_value, option_label in radio_options.iteritems():
        identifier = '%s_%s_%d' % (field.tablename, field.name, i)
        i = i + 1
        element = DIV(INPUT(_type = 'radio', _name = field.name, _value = option_value, _id = identifier, value = value, requires = requires),
                      LABEL(option_label, _for = identifier, ),
                      _class = 'afe'
                      )
        widget.append(element)
        requires = None
    return widget


def FoundationWidgetFieldsetSingleCheckbox(field, value, option):
    widget = FIELDSET(LEGEND(field.label), _class = 'fieldset no-bottom-padding')
    identifier = '%s_%s' % (field.tablename, field.name)

    element = DIV(INPUT(_type = 'checkbox', _name = field.name, _id = identifier, _value = 'on', value = value, requires = field.requires),
              LABEL(option, _for = identifier, ),
              _class = 'afe'
              )
    widget.append(element)
    return widget

def FoundationCheckbox(label, identifier, toggle_id = None, value = False):
    '''
    This function creates a simple checkbox to be used without database table.
    '''
    attributes = {'_for': identifier}
    if toggle_id:
        attributes['_data-toggle'] = toggle_id
    element = DIV(INPUT(_type = 'checkbox', _id = identifier, _name = identifier, _value = 'on', value = value),
                  LABEL(label, **attributes),
                  _class = 'afe'
              )
    return element

class ContributionCompleteness():
    '''
    This class provides all required information about the completeness status of shifts and donations.
    '''
    def __init__(self, a, t):
        if t != None and t != 0 and t > a:
            self.ratio = round(1.0*a/t*100)
            self.complete = False
            self.display_class = config.cssclass.contribactive
        else:
            self.ratio = 100
            self.complete = True
            self.display_class = config.cssclass.contribpassive

        if self.ratio < 50:
            self._class = config.cssclass.actnumberlow
        elif self.ratio < 90:
            self._class = config.cssclass.actnumbermed
        else:
            self._class = config.cssclass.actnumberhigh

        self.html = DIV('%d%% belegt' % self.ratio, _class = self._class)



def regularizeName(s):
    '''
    This function capitalizes strings like person names  in forms.
    Examples: testing/NameRegularization.py
    '''
    if not s:
        return s
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

def regularizeFormInputPersonForm(form):
    '''
    This function brings the user input to standard.
    '''
    for field in ('forename', 'name', 'street', 'place', 'zip_code'):
        if field in form.vars:
            if field == 'zip_code':
                # check zip code
                s = form.vars['zip_code']
                s = s.replace(' ', '')
                if re.search('\D', s):
                    form.errors.zip_code = 'Bitte geben Sie eine gültige Postleitzahl an.'
                form.vars['zip_code'] = s
            else:
                form.vars[field] = regularizeName(form.vars[field])

def __getDataGridRow(label, data):
    '''
    Auxiliary function for the construction of the grids below
    '''
    class_row       = 'grid-x grid-padding-x'
    class_label     = 'cell small-12 medium-4 large-3 huge-3'
    class_data      = 'cell auto'
    return DIV(DIV(label, _class = class_label), DIV(data, _class = class_data), _class = class_row)

def getPersonDataOverview(vars, type):
    '''
    This function generates a Foundation grid with person data for the confirmation pages.
    '''
    class_container = 'grid-container ' + config.cssclass.tblconfirmdata

    data_items = [
                   __getDataGridRow('Ihr Name:',            vars['forename'] + ' ' + vars['name']),
                   __getDataGridRow('Ihre Adresse:',        vars['zip_code'] + ' ' + vars['place'] + ', ' + vars['street'] + ' ' + vars['house_number']),
                   __getDataGridRow('Ihre Telefonnummer:',  vars['telephone']),
                   __getDataGridRow('Ihre E-Mail-Adresse:', vars['email']),
                ]

    if 'mail_enabled' in vars:
        data_items.extend([__getDataGridRow('Einladungen:', config.radio_options_mail_enabled[vars['mail_enabled']])])

    if 'data_use_agreed' in vars:
        data_items.extend([
                   __getDataGridRow('Persönliche Daten:', config.data_use_agreed_option[type])
            ])

    return DIV(*data_items, _class = class_container)


def getEnrolmentDataOverview(vars):
    '''
    This function generates a Foundation grid with the enrolment data (sale number, shifts, donations, etc.) for the confirmation page.
    '''
    class_container = 'grid-container ' + config.cssclass.tblconfirmdata
    data_items = [__getDataGridRow(*t) for t in vars]

    return DIV(*data_items, _class = class_container)

def getAppRequestDataOverview(vars):
    '''
    This function generates a Foundation grid with the appropriation request data for the confirmation page.
    '''
    class_container = 'grid-container ' + config.cssclass.tblconfirmdata
    data_items = [
                   __getDataGridRow('Projektbezeichung:',   vars['project']),
                   __getDataGridRow('Organisation:',        vars['organization']),
                   __getDataGridRow('Fördermittel:',        DIV(SPAN('Sie beantragen Fördermittel in Höhe von '), STRONG(str(vars['amount_requested']) + ' EUR '),
                                                                SPAN('bei Gesamtkosten des Projektes von %d EUR.' % vars['amount_total']))),
                   __getDataGridRow('Projektbeschreibung:', vars['description'])
                ]

    return DIV(*data_items, _class = class_container)

def getAppRequestDataTable(vars):
    '''
    This function generates a table containing the appropriation request data (project data) for the confirmation email.
    '''
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
                elements.append(DIV('%d. %s' % (step, element), _class = c))

            self.bar = DIV(DIV(self.label, _class = config.cssclass.progresslabel),
                           DIV(*elements,  _class = config.cssclass.progresssteps),
                           _class = config.cssclass.progressbar)

        return self.bar

