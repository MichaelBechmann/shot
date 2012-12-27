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

T.force('de')

def __validateform(form):
    '''
    Functions that take arguments or start with a double underscore are not publicly exposed and can only be called by other functions.
    This validation function checks whether or not at least one of the possible contribution checkbox fields has been checked.
    '''
    sale = Sale()
    sale.analyzecheckboxes(form.vars)
    b_contrib = False
    if (len(sale.shifts_checked) + len(sale.donations_checked)) > 0:
        b_contrib = True
    if b_contrib == False and sale.b_cannot_help_checked == False:
        form.errors.msg = T('You didn\'t check any of the contribution options! Please confirm that you cannot contribute anything.')
    elif b_contrib == True and sale.b_cannot_help_checked == True:
        form.errors.msg = T('You made an inconsistent choice! Please either check some contribution or confirm that you cannot contribute anything.')

def _contribelement(label, formname, a, t):
    '''
    This function returns a list containing the complete contribution form elements (shift or donation).
    format: [ checkbox or dummy, SPAN element with the complete label]
    '''
    try:
        r = 1.0*a/t #cast to float required
    except:
        # database may contain None for the target (during configuration)
        r =1.0   
        
    if r < 1.0:
        cl = config.cssclass.contribactive
        if r < 0.5:
            c = config.cssclass.actnumberlow
        elif r < 0.9:
            c = config.cssclass.actnumbermed
        else:
            c = config.cssclass.actnumberhigh
    else:
        c  = config.cssclass.actnumberhigh
        cl = config.cssclass.contribpassive    
   
    fe = [] # fe: form elements
    if a < t:
        # target number not reached yet => provide checkbox
        # toggle trigger class is necessary only for donations with notes active but doen't hurt for the other check boxes
        fe.append(INPUT(_type = 'checkbox', _name = formname, _class = config.cssclass.tggltrig))
    else:
        fe.append('')
    s = ' ({a}/{t}) '.format(a = a, t = t)   
    fe.append(SPAN(label, SPAN(s, _class = c), _class = cl))
    
    return fe
    

def form():
    # check whether or not the sale information form shall be displayed
    if session.form_passive:
        # The form shall be displayed for configuration purposes only.
        # Database emanipulations are not intended! 
        sale = Sale()
        l = sale.numbers.config_all()
    elif session.vendor_id == None:
        # Something went wrong.
        redirect(URL('main', 'index'))
    else:
        # The form is active.
        sale = Sale(session.vendor_id)
        l = sale.getfreenumbers()
        if sale.b_vendor_has_number:
            # The vendor already has a number for the current event.
            redirect(URL('main', 'index'))
        elif len(l) == 0:
            # There are no numbers left.
            redirect(URL('no_numbers'))
        # Finally this is the normal case!
        l.insert(0, sale.nonumber)
        
        
    # construct the form from the database tables
    formelements = []
    formelements.append(DIV(SPAN(T('My desired sale number:'), SELECT(l, _name = config.formname.sale_number)), _id = config.cssid.salenumber))
    
    # all shifts related to the current event
    formelements.append(DIV(T('I will help here:'), _class = config.cssclass.contribheading))
    
    # construct two column table of the shift elements
    # correct odd number of shifts
    if False:
        # plain table display
        se =[_contribelement(shift.label, shift.name, shift.actual_number, shift.target_number) for shift in sale.getshifts()]
        if len(se) & 1:
            se.append(['', ''])   
        formelements.append(TABLE(*[TR(se[i][0], se[i][1], se[i+1][0], se[i+1][1], _class = config.cssclass.shiftgrouptbl) for i in range(0,len(se), 2)], _id = config.cssid.contribtblshifts))

    else:
        # display shifts arranged in groups
        groups = {}
        groupheads = {}
        for shift in sale.getshifts():
            ce =_contribelement(shift.activity, shift.name, shift.actual_number, shift.target_number)
            d = shift.display
            if d not in groupheads:
                groupheads[d] = shift.timelabel
            elif session.form_passive and (groupheads[d] != shift.timelabel):
                # The shift grouped together havd different times => notify admin
                ce.append(SPAN(T('check times!!'), _class = config.cssclass.configwarn))

            if d in groups:
                groups[d].append(ce)
            else:
                groups[d] = [ce]
        
        stblgroups = []
        display = groups.keys()
        display.sort()
        for d in display:
            
            stblgroups.append(DIV(DIV(groupheads[d], _class = config.cssclass.shiftgrouphead), TABLE(*[TR(*se) for se in groups[d]]), _class = config.cssclass.shiftgrouptbl))
            
        if len(stblgroups) & 1:
            stblgroups.append('')
            
        formelements.append(TABLE(*[TR(stblgroups[i], stblgroups[i+1], _class = config.cssclass.shifttblrow) for i in range(0, len(stblgroups), 2)], _id = config.cssid.contribtblshifts))


    # all donations related to the current event
    formelements.append(DIV(T('For the cafe I will bring the following:'), _class = config.cssclass.contribheading))
    de = []
    for donation in sale.getdonations():
        a = donation.actual_number
        t = donation.target_number
        
        de.append(TR(*_contribelement(donation.label, donation.name, a, t)))
        
        # check for a < t here because if one has NoScript activa and target number is reached the notes shall not be visible
        if a < t and donation.enable_notes:
            de.append(TR('', TABLE(TR(T('I bring this:'),      INPUT(_type = 'text', _name = donation.name_note)),
                                   TR(T('Others bring this:'), SPAN(*map(LI,donation.notes))                    ),
                        _class = config.cssclass.contribnote),     _class = config.cssclass.tggl)    )
          
    formelements.append(TABLE(*de, _id = config.cssid.contribtbldons))

    formelements.append(TABLE(TR(INPUT(_type = 'checkbox', _name = config.formname.no_contrib), T('I cannot help nor bring anything!')), _id = config.cssid.nocontrib))
    
    formelements.append(TABLE(TR(
                                 T('My message:'), TEXTAREA(_type = 'text', _name = config.formname.vendor_message, _cols = 50, _rows = 3),
                                 INPUT(_type = 'submit', _class = 'button', _name = 'submit', _value = T('submit'))
                                 ), _id = config.cssid.tblsubmit))
      
    form = FORM(*formelements)   
    
   
    if session.form_passive:
        if 'submit' in request.vars:
            session.form_passive = None
            session.sale_vars = None
            redirect(URL('config', 'config_event'))    
    else:
        # pre-populate the form in case of re-direction from form_vendor_confirm() (back button pressed)
        # see book, section 'Pre-populating the form' in chapter 'Forms and Validators'
        if session.sale_vars:
            form.vars = session.sale_vars
        else:
            on = sale.getoldnumber()
            if on != None:
                form.vars[config.formname.sale_number] = on
        
        if form.validate(onvalidation = __validateform):      
            session.sale_vars = form.vars
            sale.setnumber(session.sale_vars)
            redirect(URL('confirm'))
    
        if session.sale_error_msg:
            form.errors.msg = session.sale_error_msg
            session.sale_error_msg = None
     
    return dict(form = form, id = session.vendor_id)


def confirm():
    # check if there is vendor information to be confirmed
    if (session.sale_vars == None) or (session.vendor_id == None):
        redirect(URL('main', 'index'))
    sale = Sale(session.vendor_id)
    
    # construct display of data to be confirmed
    de = [] # de: data elements
    de.append(TR(T('You are:'), sale.vendor_name))
    de.append(TR(T('Your sale number is:'), DIV(session.sale_vars[config.formname.sale_number], _id = 'sale_number')))
    
    sale.analyzecheckboxes(session.sale_vars)
    for s in sale.getcheckedshifts():
        de.append(TR(T('You help here:'), DIV(s.day + ', ' + s.time + ', ' + s.activity)))
    for d in sale.getcheckeddonations():
        out =  d.item
        if d.note != None:
            out += ' (' + d.note + ')'
        de.append(TR(T('You bring this:'), DIV(out)))
    
    if sale.b_cannot_help_checked:
        de.append(TR('Schade:', DIV(T('Sie können leider nicht helfen.'))))
    
    if session.sale_vars[config.formname.vendor_message]:
        de.append(TR(T('You left a message:'), session.sale_vars[config.formname.vendor_message]))

    
    data = TABLE(*de)
        
    
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
        try:  
            # Add submitted information to database record.
            sale.setdbentries(session.sale_vars)
        
            # prevent multiple database entries
            session.clear()
                
            # send mail with sale number
            sale.sendnumbermail()
            nextpage = URL('final')
            
        except:
            '''
            If the number to be added is already in the table for some reason the 'unique' attribute of the field 'number'
            causes an exception.
            '''
            session.sale_vars.number = None     # Do not pre-populate form with number which is already assigned!
            session.sale_error_msg = T('Oops! Your sale number has just been assigned to someone else. Please choose another one.')
            nextpage = URL('form')
            
        redirect(nextpage)      
        
    return(dict(form = form, data = data))

def final():
    return dict()

def no_numbers():
    return dict()


class Sale():
    '''
    This class provides methods for handling all sale related information like sale numbers or help information.
    These methods include all interaction with the database.
    
    argument: vid - vendor id
    '''
    def __init__(self, vid = 0):  
        self.currentevent = shotdb(shotdb.event.active == True).select().last().id
        self.vid = vid
        if self.vid > 0:
            self.vendor_name = shotdb.vendor(session.vendor_id).forename + ' ' + shotdb.vendor(session.vendor_id).name
            if self._salenumber() == None:
                self.b_vendor_has_number = False
            else:
                self.b_vendor_has_number = True
        else:
            self.vendor_name = 'anonymous'
        self.nonumber = ' - '
        self.b_cannot_help_checked = False
        self.numbers = Numbers(shotdb, self.currentevent)
        self.freenumbers = []

    def getfreenumbers(self):
        '''
        This method returns a list of all still free numbers.
        The result depends on the vendor(kindergarten or not).
        '''          
        if shotdb.vendor(self.vid).kindergarten != config.no_kindergarten_id:
            self.freenumbers = self.numbers.free_kg()
        else:    
            self.freenumbers = self.numbers.free()
        return(self.freenumbers)
    
    def getoldnumber(self):
        '''
        This method tries to retrieve the sale number the vendor had at the last event
        '''
        n = None
        query = (shotdb.sale.event == (self.currentevent - 1)) & (shotdb.sale.vendor == self.vid)
        rows = shotdb(query).select()
        if rows:
            n = rows.last().number
            if n not in set(self.freenumbers):
                n = None
        return n

    def setnumber(self, vars):
        '''
        This function checks if a sale number has been chosen.
        If not the number is assigned automatically. Note that the form.vars object passes to this function (by reference) is modified!
        To keep track of the user input a new boolean field is added.
        '''
        vars.number_assigned = False
        if vars[config.formname.sale_number] == self.nonumber:
            vars.number_assigned = True
            vars[config.formname.sale_number] = self.getfreenumbers()[-1]
              
    def getshifts(self):
        '''
        This function retrieves all shifts belonging to the current event and adds some evaluated properties.
        '''
        self.rows = shotdb(shotdb.shift.event == self.currentevent).select()
        for r in self.rows:
            r.timelabel = r.day + ', ' + r.time
            r.label     = r.day + ', ' + r.time + ', ' + r.activity
            # add name of the form element, format: configured marker name '$' database id
            r.name  = config.formname.shift + '$' + str(r.id)
        
        # Note: Here a reference is returned!
        return self.rows

    def getdonations(self):
        '''
        This function retrieves all donations belonging to the current event and adds some evaluated properties.
        '''
        self.rows = shotdb(shotdb.donation.event == self.currentevent).select()
        for r in self.rows:
            r.label = r.item
            
            # add name for the form element, format: configured marker name '$' database id
            r.name  = config.formname.donation + '$' + str(r.id)
            
            # add name for the form element, format: configured marker name '$' database id of donation
            r.name_note = config.formname.note + '$' +  str(r.id)
            
            # add a list of all notes which already exist for this donation
            r.notes = []
            for bring in shotdb(shotdb.bring.donation == r.id).select():
                if bring.note != None:
                    r.notes.append(bring.note)
            
        # Note: Here a reference is returned!
        return self.rows
    
    def analyzecheckboxes(self, vars):
        '''
        This method analyzes which checkboxes of the are checked.
        For the shifts list of the related database ids are constructed.
        For the donations a dictionary is generated containing also the notes:
            {donation id: note}; None if there is no note
        The 'no contribution' checkbox a translates to a boolean.
        '''
        self.shifts_checked = []
        self.donations_checked = {}
        # iterate through the dictionary 'vars' containing the form elements
        # for the form elements which have been checked => decode the database table and the id from the key
        p = re.compile('^([a-z]+)\$([0-9]+)$')
        for (k, v) in vars.iteritems():
            if v == 'on':
                m = p.match(k)
                if m:
                    table = m.group(1)
                    id = int(m.group(2))
                    if table == config.formname.shift:
                        self.shifts_checked.append(id)
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
                        
        if vars[config.formname.no_contrib] == 'on':
            self.b_cannot_help_checked = True

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
        for r in rows:
            r.note = self.donations_checked[r.id]
    
        return rows

    def setdbentries(self, vars):
        '''
        This method creates all database entries related to the sale (sale number, shifts, donations, message).
        '''
        self.analyzecheckboxes(vars)
        
        # sale number
        sid = shotdb.sale.insert(event = self.currentevent, vendor = self.vid, number = vars[config.formname.sale_number], number_assigned = vars.number_assigned) 
        
        # add log info to vendor
        s = 'sale # ' + str(sid) + ' added'
        Log(shotdb).vendor(self.vid, s)
        
        # message
        if vars[config.formname.vendor_message] != '':
            shotdb.message.insert(event = self.currentevent, vendor = self.vid, text = vars[config.formname.vendor_message]) 
        
        # shifts
        for id in self.shifts_checked:
            shotdb.help.insert(shift = id, vendor = self.vid)
            
        # donations
        for (id, note) in self.donations_checked.iteritems():
            shotdb.bring.insert(donation = id, vendor = self.vid, note = note)
    
    def _salenumber(self):
        '''
        This method determines the sale number for the vendor and the current event fromthe database.
        '''
        query = (shotdb.sale.event == self.currentevent) & (shotdb.sale.vendor == self.vid)
        r = shotdb(query).select(shotdb.sale.number).last()
        if r != None:
            n = r.number
        else:
            n = None
        return n
    
    def sendnumbermail(self):
        '''
        This method collects all information for the number mail to be sentto the vendor.
        Unlike the pages before the mail contains the data from the database not from the forms!
        '''
        vendor = shotdb.vendor(self.vid)
        
        # retrieve sale number
        number = self._salenumber()
        
        # retrieve help information
        query = (shotdb.help.shift == shotdb.shift.id) & (shotdb.help.vendor == self.vid) & (shotdb.shift.event == self.currentevent)
        cl =  ['Sie helfen: ' + r.shift.day + ', ' + r.shift.time + ', ' + r.shift.activity for r in shotdb(query).select()]
        
        # retrieve bring information
        query = (shotdb.bring.donation == shotdb.donation.id) & (shotdb.bring.vendor == self.vid) & (shotdb.donation.event == self.currentevent)
        for r in shotdb(query).select():
            d = 'Sie bringen mit: ' + r.donation.item
            if r.bring.note != None:
                d += ' (' + r.bring.note + ')'
            cl.append(d)
        
        if len(cl) > 0:
            contributions = UL(*cl)
        else:
            contributions = 'Sie können leider nicht helfen.'
        
        NumberMail(vendor, str(number), str(contributions)).send()
        