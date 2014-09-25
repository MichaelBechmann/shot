# -*- coding: utf-8 -*-
'''
This file contains everything related to the sale data (sale number, contributions, etc.).
'''
# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb
    
from shotmail import *
from shotdbutil import *
import re
from shoterrors import ShotError
from formutils import regularizeName, getActNumberRatio


T.force('de')

def __validateform(form):
    '''
    Functions that take arguments or start with a double underscore are not publicly exposed and can only be called by other functions.
    This validation function checks whether or not at least one of the help shift checkbox fields has been checked.
    Notes on donations are regularized.
    '''
    sale = Sale()
    sale.analyzecheckboxes(form.vars)
    if sale.b_does_help == False and sale.b_cannot_help == False:
        form.errors.msg = 'Sie haben sich für keine Helferschicht eingetragen. Bitte bestätigen Sie, daß Sie nicht helfen können.'
    elif sale.b_does_help == True and sale.b_cannot_help == True:
        form.errors.msg = 'Sie haben widersprüchliche Angaben gemacht! Bitte tragen Sie sich entweder für eine Helferschicht ein oder markieren Sie, daß Sie nicht helfen können.'
    
    for donation in sale.getdonations():
        if donation.name_note in form.vars:
            form.vars[donation.name_note] = regularizeName(form.vars[donation.name_note])
        
def __contribelement(label, formname, a, t):
    '''
    This function returns a list containing the complete contribution form elements (shift or donation).
    format: [ checkbox or dummy, SPAN element with the complete label]
    '''
    # database may contain None for the target (during configuration)
    if t != None and t > a:
        tmp = getActNumberRatio(a, t)
        r = tmp['ratio']
        c  = tmp['_class']
        cl = config.cssclass.contribactive
    else:
        r = 100
        c  = config.cssclass.actnumberhigh
        cl = config.cssclass.contribpassive    
   
    fe = [] # fe: form elements
    if a < t:
        # target number not reached yet => provide checkbox
        # toggle trigger class is necessary only for donations with notes active but doen't hurt for the other check boxes
        fe.append(INPUT(_type = 'checkbox', _name = formname, _class = config.cssclass.tggltrig))
    else:
        fe.append('')
    s = ' (%d%% belegt) ' % r   
    fe.append(SPAN(label, SPAN(s, _class = c), _class = cl))
    
    return fe
    

def form():
    # check whether or not the sale information form shall be displayed
    if session.form_passive:
        # The form shall be displayed for configuration purposes only.
        # Database manipulations are not intended! 
        sale = Sale()
    elif session.registration_person_id == None:
        # Something went wrong.
        redirect(URL('main','index'))
        #raise ShotError('Sale form entered without identified person.') # see issue #43
    else:
        # The form is active.
        sale = Sale(session.registration_person_id)
            
    # construct the form from the database tables
    formelements = []
    
    elem_sale_number = TABLE(TR(INPUT(_type = 'checkbox', _name = config.formname.sale_number, _checked = 'checked',_value = 'on'), 'Ich möchte eine Kommissionsnummer haben.'), _id = config.cssid.salenumberform)
    elem_status = TABLE(TR('Aktueller Status:', WaitList(shotdb).status_text(session.registration_person_id)), _id = config.cssid.salenumberstatus)
    formelements.append(DIV(elem_sale_number, elem_status,  _id = config.cssid.salenumber))
    
    formelements.append(TABLE(TR(INPUT(_type = 'checkbox', _name = config.formname.no_contrib), 'Ich kann leider keine Helferschicht übernehmen.'), _id = config.cssid.nocontrib))
    formelements.extend([BR(), BR()])
    # all shifts related to the current event
    formelements.append(DIV('Ich kann folgende Helferschicht(en) übernehmen:', _class = config.cssclass.contribheading))

    # display shifts arranged in groups
    groups = {}
    groupheads = {}
    for shift in sale.getshifts():
        a = shift.actual_number
        t = shift.target_number
        ce =__contribelement(shift.activity, shift.name, a, t)
        d = shift.display
        if d not in groupheads:
            groupheads[d] = shift.timelabel
        elif session.form_passive and (groupheads[d] != shift.timelabel):
            # The shift grouped together have different times => notify admin
            ce.append(SPAN(T('check times!!'), _class = config.cssclass.configwarn))

        if d in groups:
            groups[d].append(TR(ce))
        else:
            groups[d] = [TR(ce)]
            
        if(a < t and shift.comment != None and shift.comment != ''):
            groups[d].append(TR('', TD(shift.comment, _class = config.cssclass.shiftcomment), _class = config.cssclass.tggl))
    
    stblgroups = []
    display = groups.keys()
    display.sort()
    for d in display:
        stblgroups.append(DIV(DIV(groupheads[d], _class = config.cssclass.shiftgrouphead), TABLE(*groups[d]), _class = config.cssclass.shiftgrouptbl))
        
    if len(stblgroups) & 1:
        stblgroups.append('')
        
    formelements.append(TABLE(*[TR(stblgroups[i], stblgroups[i+1], _class = config.cssclass.shifttblrow) for i in range(0, len(stblgroups), 2)], _id = config.cssid.contribtblshifts))

    # all donations related to the current event
    formelements.append(DIV('Für das Café bringe ich folgendes mit (sofern ich eine Kommissionsnummer erhalte):', _class = config.cssclass.contribheading))
    de = []
    for donation in sale.getdonations():
        a = donation.actual_number
        t = donation.target_number
        
        de.append(TR(*__contribelement(donation.label, donation.name, a, t)))
        
        # check for a < t here because if one has NoScript active and target number is reached the notes shall not be visible
        if (a < t and donation.enable_notes):
            de.append(TR('', TABLE(TR(T('I bring this:'),      INPUT(_type = 'text', _name = donation.name_note)),
                                   TR(T('Others bring this:'), SPAN(*map(LI,donation.notes))                    ),
                        _class = config.cssclass.contribnote),     _class = config.cssclass.tggl)    )
          
    formelements.append(TABLE(*de, _id = config.cssid.contribtbldons))

    formelements.append(TABLE(TR(
                                 T('My message:'), TEXTAREA(_type = 'text', _name = config.formname.person_message, _cols = 50, _rows = 3),
                                 INPUT(_type = 'submit', _class = 'button', _name = 'submit', _value = T('submit'))
                                 ), _id = config.cssid.tblsubmit))
      
    form = FORM(*formelements)   
    
   
    if session.form_passive:
        if 'submit' in request.vars:
            session.form_passive = None
            session.sale_vars = None
            redirect(URL('config', 'config_event'))    
    else:
        # pre-populate the form in case of re-direction from confirmation page (back button pressed)
        # see book, section 'Pre-populating the form' in chapter 'Forms and Validators'
        if session.sale_vars:
            form.vars = session.sale_vars
        
        if form.validate(onvalidation = __validateform):      
            session.sale_vars = form.vars
            redirect(URL('confirm'))
    
        if session.sale_error_msg:
            form.errors.msg = session.sale_error_msg
            session.sale_error_msg = None
    
    return dict(announcement = sale.announcement, form = form, template_set = sale.template_set)


def confirm():
    # check if there is personal information to be confirmed
    if (session.sale_vars == None) or (session.registration_person_id == None):
        redirect(URL('main','index'))
    sale = Sale(session.registration_person_id)
    
    # construct display of data to be confirmed
    de = [] # de: data elements
    de.append(TR('Ich bin:', sale.person_name))
    
    sale.analyzecheckboxes(session.sale_vars)
    
    if sale.b_wants_sale_number:
        de.append(TR('', 'Ich möchte eine Kommissionsnummer haben für den %s.' % sale.announcement))
        if sale.b_cannot_help:
            de.append(TR('', TD('(Hinweis: %s)' % WaitList(shotdb).status_text(session.registration_person_id), _class = config.cssclass.confirmcomment)))
    else:
        de.append(TR('', TD('Ich möchte ', STRONG('keine'), ' Kommissionsnummer haben.')))
    
    for s in sale.getcheckedshifts():
        de.append(TR(TD('Hier helfe ich:'), TD(s.day + ', ' + s.time + ', ' + s.activity)))
        if(s.comment != None and s.comment != ''):
            de.append(TR('', TD('('+s.comment+')', _class = config.cssclass.shiftcomment)))
    
    if sale.b_cannot_help:
        de.append(TR('', TD('Ich kann leider keine Helferschicht übernehmen.')))        
    
    for d in sale.getcheckeddonations():
        out =  d.item
        if d.note != None:
            out += ' (' + d.note + ')'
        de.append(TR('Das bringe ich mit:', out))
    
    if sale.b_cannot_donate:
        de.append(TR('', TD('Ich kann leider nichts für das Café spenden.')))

    
    if session.sale_vars[config.formname.person_message]:
        de.append(TR('Meine Nachricht:', session.sale_vars[config.formname.person_message]))

    
    data = TABLE(*de, _class = config.cssclass.tblconfirmdata)
        
    
    # The _name arguments are important as the one of the pressed button will appear in request.vars.
    form = FORM(TABLE(TR(
                         INPUT(_type = 'submit', _class = 'button', _name = 'submit back', _value = T('back')),
                         INPUT(_type = 'submit', _class = 'button', _name = 'submit send', _value = T('go!')), _id = config.cssid.waitmsgtrig)
                        ),
                DIV(T(config.msg.wait), _id = config.cssid.waitmsg)
                )
        
    if 'submit back' in request.vars:
        redirect(URL('form'))
        
    elif 'submit send' in request.vars:
        # Add the sale information to the database and send mail:
            # Add submitted information to database record.
        sale.setdbentries()
        
        # prevent multiple database entries
        session.clear()
        if sale.b_sale_number_assigned or not sale.b_wants_sale_number:
            redirect(URL('sale','final'))
        else:
            redirect(URL('sale','final_wait'))
        
    return(dict(form = form, data = data))

def final():
    return dict()

def final_wait():
    return dict()

def no_numbers():
    return dict()


class Sale():
    '''
    This class provides methods for handling all sale related information like sale numbers or help information.
    These methods include all interaction with the database.
    
    argument: pid - person id
    '''
    def __init__(self, pid = 0): 
        self.pid = pid
        
        e = Events(shotdb)
        self.announcement = e.get_current_announcement(b_include_time = False)
        self.currentevent_id = e.current.event.id
        self.template_set = e.current.event.template_set
        
        self.contrib = Contributions(shotdb, self.currentevent_id)
        
        self.person_name = 'anonymous'
        
        rows = shotdb(shotdb.person.id == self.pid).select()
        if len(rows) > 0:
            person = rows.last()
            # get name of the person
            self.person_name = person.forename + ' ' + person.name
              
    def getshifts(self):
        '''
        This function retrieves all shifts belonging to the current event and adds some evaluated properties.
        '''
        rows = self.contrib.get_shifts()
        for r in rows:
            r.timelabel = r.day + ', ' + r.time
            r.label     = r.day + ', ' + r.time + ', ' + r.activity
            # add name of the form element, format: configured marker name '$' database id
            r.name  = config.formname.shift + '$' + str(r.id)
        
        # Note: Here a reference is returned!
        return rows

    def getdonations(self):
        '''
        This function retrieves all donations belonging to the current event and adds some evaluated properties.
        '''
        rows = self.contrib.get_donations()
        for r in rows:
            r.label = r.item
            
            # add name for the form element, format: configured marker name '$' database id
            r.name  = config.formname.donation + '$' + str(r.id)
            
            # add name for the form element, format: configured marker name '$' database id of donation
            r.name_note = config.formname.note + '$' +  str(r.id)
            
            # add a list of all notes which already exist for this donation
            r.notes = self.contrib.get_notes_list_for_donation(r.id)
            
        # Note: Here a reference is returned!
        return rows
    
    def analyzecheckboxes(self, vars):
        '''
        This method analyzes which checkboxes of the form are checked.
        For the shifts list of the related database ids are constructed.
        For the donations a dictionary is generated containing also the notes:
            {donation id: note}; None if there is no note
        The 'want sale number' and 'no contribution' checkbox translate to boolean.
        '''
        self.vars = vars
        self.shifts_checked = []
        self.b_does_help = False
        self.donations_checked = {}
        # iterate through the dictionary 'vars' containing the form elements
        # for the form elements which have been checked => decode the database table and the id from the key
        p = re.compile('^([a-z]+)\$([0-9]+)$')
        for (k, v) in self.vars.iteritems():
            if v == 'on':
                m = p.match(k)
                if m:
                    table = m.group(1)
                    id = int(m.group(2))
                    if table == config.formname.shift:
                        self.shifts_checked.append(id)
                        self.b_does_help = True
                    elif table == config.formname.donation:
                        self.donations_checked[id] = None
                        
        p = re.compile('^{n}\$([0-9]+)$'.format(n = config.formname.note))
        for (k, v) in vars.iteritems():
            if v != '':
                m = p.match(k)
                if m:
                    did = int(m.group(1)) # 'donation-id'
                    # There may well be notes without the corresponding donation being checked!
                    if did in self.donations_checked:
                        self.donations_checked[did] = v
                                                
        if self.vars[config.formname.sale_number] == 'on':
            self.b_wants_sale_number = True
        else:
            self.b_wants_sale_number = False
                        
        if self.vars[config.formname.no_contrib] == 'on':
            self.b_cannot_help = True
        else:
            self.b_cannot_help = False

    def getcheckedshifts(self):
        '''
        This method retrieves from the database all shifts which have been checked in the sale form.
        Note: The method analyzeckeckboxes() must be executed before!
        '''
        return  shotdb(shotdb.shift.id.belongs(self.shifts_checked)).select()

    def getcheckeddonations(self):
        '''
        This method retrieves from the database all donations which have been checked in the sale form.
        If there is a corresponding note, this is added to the row object.
        Note: The method analyzeckeckboxes() must be executed before!
        '''
        dids = self.donations_checked.keys() # donation ids
        rows = shotdb(shotdb.donation.id.belongs(dids)).select()
        self.b_cannot_donate = True
        for r in rows:
            r.note = self.donations_checked[r.id]
            self.b_cannot_donate = False
            
        return rows

    def setdbentries(self):
        '''
        This method creates all database entries related to the sale (sale number, shifts, donations, message).
        '''
        # shifts
        for sid in self.shifts_checked:
            shotdb.help.update_or_insert(shift = sid, person = self.pid)
            
        # donations
        for (did, note) in self.donations_checked.iteritems():
            shotdb.bring.update_or_insert(donation = did, person = self.pid, note = note)
            
        # message
        if self.vars[config.formname.person_message] != '':
            shotdb.message.insert(event = self.currentevent_id, person = self.pid, text = self.vars[config.formname.person_message])
        
        
        # sale numbers
        self.b_sale_number_assigned = False
        if self.b_wants_sale_number:
            # set person on wait list
            shotdb.wait.update_or_insert(event = self.currentevent_id, person = self.pid)
            if (self.b_does_help):
                # person gets sale number
                if NumberAssignment(shotdb, self.pid).assign_number() > 0:
                    # sale number has been assigned successfully or person already has a sale number
                    shotdb.commit()
                    NumberMail(shotdb, self.pid).send()
                    self.b_sale_number_assigned = True

            if self.b_sale_number_assigned == False:
                # person shall not be assigned a sale number or assignment failed (no free numbers left)
                # send wait list mail
                shotdb.commit()
                WaitMail(shotdb, self.pid).send()
        else:
            shotdb.commit()
            NumberMail(shotdb, self.pid).send()
        