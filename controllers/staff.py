# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0:
    from gluon import *
    from gluon.languages import translator as T
    global request
    global response
    global session
    global shotdb
    global SQLField
    global auth

from shotdbutil import *
from gluon.tools import Crud
from shoterrors import ShotError
from formutils import *
from shotmail import *
import re

T.force('de')

@auth.requires_membership('staff')
def person_summary():
    form = SQLFORM.factory(SQLField('person', label='Select a person', requires=IS_IN_DB(shotdb,'person.id', '%(name)s, %(forename)s (%(place)s)', orderby=shotdb.person.name)),
                           buttons = [SPAN(INPUT(_type = 'submit', _class = 'button', _value = 'display'), _class = 'js_hide')]
                           )
    form.custom.widget.person['_class'] = 'autosubmit'

    # prepopulate form
    if session.selected_pid != None:
        pid = session.selected_pid
        form.vars['person'] = pid
    else:
        pid = 0
    
    # prosess form
    if form.process().accepted:
        pid = int(form.vars['person'])
        session.selected_pid = pid
        session.mailform_message = None
        # redirect is necessary to pre-populate the form; didn't find another way
        redirect(request.env.request_uri.split('/')[-1])
    
    p = Person(shotdb, pid)
    if p.record != None:
        
        tu = TableUtils()
        
        # initialise flags indicating which email actions shall be available 
        b_person_has_number      = False
        b_person_is_on_waitlist  = False
        b_person_helps_or_brings = False       
        
        # person information
        name = A(DIV(DIV('%s, %s'% (p.record.name, p.record.forename), _id = 'ps_name'), DIV(CENTER('(#%d)'%( p.record.id), _id = 'ps_id'))),
                 _href = URL('staff', 'crud/person/edit/%d/ps'%( p.record.id)))
        if p.record.verified != None and p.record.verified > 0:
            email_verify_note = SPAN('verified', _class = 'ps_email_active')
        else:
            email_verify_note = SPAN('not verified', _class = 'ps_email_inactive')
            
        if p.record.mail_enabled != False:
            email_enable_note = SPAN('active', _class = 'ps_email_active')
        else:
            email_enable_note = SPAN('inactive', _class = 'ps_email_inactive')
    
        info = TABLE(
                     TR('Adress:', '%s, %s, %s %s' %(p.record.place, p.record.zip_code, p.record.street, p.record.house_number)),
                     TR('Phone:', p.record.telephone),
                     TR('Email:', TD(SPAN('%s (' % (p.record.email)), email_verify_note, SPAN(', '), email_enable_note, SPAN(')'))),
                     )
        log = DIV(p.record.log, _id = 'ps_log')
        
        # table with person activity data
        col_conf = (('numbers', 'sale'),
                    ('wait entries', 'wait'),
                    ('shifts', 'help'),
                    ('donations', 'bring'),
                    ('messages', None)
                    )
        data_elements = []
        for ed in p.eventdata:
            e = TD(ed['label'])
            cols = []
            for col, table in col_conf:
                if col in ed:
                    elems = []
                    for x in ed[col]:
                        if table == None:
                            elems.append(DIV(x[1]))
                        else:
                            elems.append(DIV(A(x[1], _href = URL('staff','crud/%s/edit/%d/ps' % (table, x[0]))), _class = 'ps_' + table))
                    
                    if ed['current']:
                        if (col in ('shifts', 'donations') or (col in ('numbers', 'wait entries') and len(elems) == 0)):
                            if col == 'numbers':
                                elems.append(DIV('prediction: %d' % (NumberAssignment(shotdb, pid).determine_number()), _id = 'ps_prediction'))

                            elems.append(A('+', _href = URL('staff','crud/%s/add/ps' % (table)), _class = 'ps_add_link'))
                            
                        # evaluate email action flags
                        if len(ed['shifts']) > 0 or len(ed['donations']) > 0:
                            b_person_helps_or_brings = True
                        if len(ed['numbers']) > 0:
                            b_person_has_number = True
                        if len(ed['wait entries']) > 0:
                            b_person_is_on_waitlist = True                       

                cols.append(TD(DIV(*elems)))

            data_elements.append(TR(e, *cols, _class = tu.get_class_evenodd()))

        data = TABLE(THEAD(TR(TH('Event'), *[TH(c[0].capitalize()) for c in col_conf])),
                     TBODY(*data_elements), _class = 'list', _id = 'ps_data_table')

        # mail actions
        tu.reset()
        mail_conf = ((0, 'Free text mail',                              PlainMail,                          True), 
                     (1, 'Invitation mail',                             InvitationMail,                     True), 
                     (2, 'Registration mail',                           RegistrationMail,                   True),
                     (3, 'Sale number and contribution mail',           NumberMail,                         b_person_has_number),
                     (4, 'Reminder mail',                               ReminderMail,                       b_person_helps_or_brings or b_person_has_number),
                     (5, 'Wait list mail',                              WaitMail,                           b_person_is_on_waitlist),
                     (6, 'Wait list denial mail',                       WaitDenialMail,                     b_person_is_on_waitlist),
                     (7, 'Sale number from waitlist mail',              NumberFromWaitlistMail,             b_person_is_on_waitlist),
                     (8, 'Sale number from waitlist as successor mail', NumberFromWaitlistMailSuccession,   b_person_is_on_waitlist),
                     )

        rows = [TR(m[1],
                   *[
                     INPUT(_type = 'submit', _name = 'p_' + str(m[0]), _value = T('preview')),
                     INPUT(_type = 'submit', _name = 's_' + str(m[0]), _value = T('send'), _class = 'irreversible')
                    ]
                    if m[3] 
                    else [TD('preview', _class = 'ps_inactive'), TD('send', _class = 'ps_inactive')], _class = tu.get_class_evenodd()) 
                    for m in mail_conf]

        mailform = FORM(TABLE(TR(TD(TABLE(*rows, _class = 'list')),
                        TD('Append a message:', BR(), TEXTAREA(_type = 'text', _name = 'message', _cols = 20, _rows = 10))), _id = 'ps_mail_table'))

        # restore message text
        if session.mailform_message != None:
            mailform.vars['message'] = session.mailform_message

        if mailform.validate():
            for p in request.vars.iterkeys():
                m = re.match('([ps])_(\d+)', p)
                if m:
                    idx = int(m.group(2))
                    mail = mail_conf[idx][2](shotdb, pid)
                    if idx == 0:
                        mail.add_body(request.vars['message'])
                    else:
                        mail.add_appendix(request.vars['message'])
                    if m.group(1) == 'p':
                        session.mailform_message = request.vars['message']
                        return mail.get_preview()

                    else:
                        mail.send()
                        session.mailform_message = None
                        redirect(URL('mail_sent'))

    else:
        name        = None
        info        = None
        log         = None
        data        = None
        mailform    = None

    return dict(form = form, mailform = mailform, name = name, info = info, log = log, data = data)

def mail_sent():
    return dict()

@auth.requires_membership('team')
def dashboard():
    e = Events(shotdb)
    n = Numbers(shotdb, e.current.event.id)
    w = WaitList(shotdb)
    c = Contributions(shotdb, e.current.event.id)
    
    return dict(event           = e.current.form_label,
                n_assigned      = n.number_of_assigned(),
                n_wait          = w.length(),
                n_limit         = e.current.event.numbers_limit,
                n_shifts        = c.get_number_of_shifts(),
                n_donations     = c.get_number_of_donations(),
                shifts          = c.get_shifts(),
                donations       = c.get_donations()
                )



@auth.requires_membership('staff')
def table():
    options = {}
    t = request.args(0)
    if(t == 'person'):
        query = shotdb.person.id > 0
        options['displayeventfilter'] = False
        
    elif(t == 'help'):
        query  = (shotdb.help.person == shotdb.person.id)
        query &= (shotdb.help.shift  == shotdb.shift.id)
        options['eventtable'] = 'shift'
        
    elif(t == 'bring'):
        query =  (shotdb.bring.person   == shotdb.person.id)
        query &= (shotdb.bring.donation == shotdb.donation.id)
        options['eventtable'] = 'donation'
        
    elif(t == 'message'):
        query = (shotdb.message.person == shotdb.person.id)
    
    elif(t == 'sale'):
        query = (shotdb.sale.person == shotdb.person.id)
    
    elif(t == 'wait'):
        query = (shotdb.wait.person == shotdb.person.id)
        options['left'] = shotdb.sale.on((shotdb.wait.person == shotdb.sale.person) & (shotdb.wait.event == shotdb.sale.event))
    
    elif(t == 'request'):
        query = shotdb.request.id > 0
        options['displayeventfilter'] = False
        
    elif(t == 'shift'):
        query = (shotdb.shift.id > 0)
    
    elif(t == 'donation'):
        query = (shotdb.donation.id > 0)

    else:
        return 'Invalid table!'
    
    
    f = Filter(t, query, **options)
    return dict(table = t, form = f.form, sqltab = f.sqltab)


@auth.requires_membership('staff')
def crud():
    
    tablename = request.args(0)
    action = request.args(1)
    id = request.args(2)
    
    if request.args(-1) == 'ps':
        # crud functions are called from person summary page
        return_page = URL('person_summary')
        pid = session.selected_pid
        
    else:
        return_page = URL('table/' + tablename)
        pid = None
     
    crud = Crud(shotdb)
    crud.settings.auth = auth   # ensures access control via permissions
    crud.settings.controller = 'staff'
    crud.settings.create_next = return_page
    crud.settings.update_next = return_page
    crud.settings.update_deletable = True
    crud.settings.showid = True   
    
    if(action == 'add'):
        if pid != None:
            shotdb[tablename].person.default = pid
            shotdb[tablename].person.writable = False
            if 'event' in shotdb[tablename]:
                shotdb[tablename].event.default = Events(shotdb).current.event.id
                shotdb[tablename].event.writable = False
                
        crud_response = crud.create(tablename)
        
    elif(action == 'edit' and id != None):
        if shotdb[tablename].has_key('person'):
            shotdb[tablename].person.writable = False
        crud_response = crud.update(tablename, id)
    else:
        crud_response = 'Nothing selected!'
    
    return dict(crud_response = crud_response)

class Filter():
    '''
    This class provides everything to add filter functions for all tables.
    '''
    
    def __init__(self, tablename, query, left = None, displayeventfilter = True, eventtable = None):
        '''
        The argument eventtable must only be given if the main table 'table' does not contain the event-id itself.
        '''
        self.tablename = tablename
        self.table = getattr(shotdb, self.tablename)
        self.displayeventfilter = displayeventfilter
        if eventtable != None:
            self.eventtable = getattr(shotdb, eventtable)
        else:
            self.eventtable = self.table
        
        self.query = query
        self.left  = left
        
        label_all = 'all events'
        name_event  = 'selev'
        name_colset = 'selcs'
          
        self.e = Events(shotdb)
        self.e.get_all()
        le = self.e.all.keys()
        le.insert(0, label_all)
        
        ls = config.colsets[self.tablename]['sets'].keys()
        
        # provide edit links
        shotdb[self.tablename].id.represent = lambda id, row: A(id,_href=URL('crud/' + self.tablename + '/edit', args=(id)))
        
        formelements = []
        if self.displayeventfilter:
            formelements.append(SPAN(T('event:'),   SELECT(le, _name = name_event, _class = 'autosubmit')))
        formelements.append(SPAN(T('column set:'),  SELECT(ls, _name = name_colset, _class = 'autosubmit')))
        formelements.append(SPAN(INPUT(_type = 'submit', _class = 'button', _value = T('display')), _class = 'js_hide'))
        formelements.append(DIV(BR(), A('Click here to add new entry!',_href=URL('staff/crud', self.tablename, 'add'))))
        self.form = FORM(*formelements)

        # extract selections from session object for use in the controller and pre-populate selectors
        # event filter selection
        selev = session.selected_event
        if selev != None:
            self.form.vars[name_event] = selev
            if selev == label_all:
                self.event_id = 0
            else:
                self.event_id = self.e.all[selev]
        else:
            self.form.vars[name_event] = self.e.current.form_label
            self.event_id = self.e.current.event.id 

        
        # column set selection    
        if session.selected_colsets != None and session.selected_colsets.has_key(self.tablename):
            cs = session.selected_colsets[self.tablename]           
        else:
            cs = config.colsets[self.tablename]['default']
        self.form.vars[name_colset] = cs
        self.colset = config.colsets[self.tablename]['sets'][cs]
        
        # process form
        if self.form.process().accepted:
            session.selected_event = self.form.vars[name_event]
            if session.selected_colsets == None:
                session.selected_colsets = {}
            session.selected_colsets[self.tablename] = self.form.vars[name_colset]
            
            # redirect is necessary to pre-populate the form; didn't find another way
            redirect(request.env.request_uri.split('/')[-1])
        
        # construct the query for the selected event
        if self.displayeventfilter:
            if self.event_id > 0:
                queryevent = self.eventtable.event == self.event_id
            else:
                queryevent = self.eventtable.id > 0
            self.query &= queryevent    

        # get the sorting column from the selected column head   
        if request.vars.orderby:                
            if session.sort_column.has_key(self.tablename) and session.sort_column[self.tablename]== request.vars.orderby:
                # table is already sorted for this very column => sort in reverse order
                # due to the '~' operator for reverse sorting the database field must be constructed (no better solution so far)
                aux = request.vars.orderby.split('.')
                self.orderby = ~getattr(getattr(shotdb,aux[-2]),aux[-1])
                del session.sort_column[self.tablename]
            else:
                # here the string is sufficient
                self.orderby = request.vars.orderby
                session.sort_column[self.tablename] = request.vars.orderby
        else:
            self.orderby = self.table.id
            session.sort_column = {self.tablename: self.tablename + '.id'} 
            
            
        # construct table
        self.sqltab = SQLTABLE(shotdb(self.query).select(left = self.left, orderby = self.orderby),
                               columns = self.colset,
                               headers = 'fieldname:capitalize', orderby = 'dummy', _class = 'list')

        
    