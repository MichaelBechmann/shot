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
from gluon.storage import Storage
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
    if request.args(0):
        pid = int(request.args(0))
        form.vars['person'] = pid
        session.selected_pid = pid
        
    elif session.selected_pid:
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
        redirect(URL('person_summary'))
    
    
    p = Person(shotdb, pid)
    if p.record != None:

        tu = TableUtils()
        
        # initialise flags indicating which email actions shall be available 
        b_person_has_number      = False
        b_person_is_on_waitlist  = False
        b_person_helps_or_brings = False       
        
        # person information
        name = A(DIV(DIV('%s, %s'% (p.record.name, p.record.forename), _id = 'ps_name'), DIV(CENTER('(#%d)'%( p.record.id), _id = 'ps_id'))),
                 _href = URL('crud',args = ['person', 'edit'], vars = dict(id = p.record.id)))
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
                            elems.append(DIV(A(x[1], _href = URL('crud', args = [table, 'edit'], vars = dict(eid = ed['eid'], id = x[0]))), _class = 'ps_' + table))
                    
                    if ed['current']:
                        if (col in ('shifts', 'donations') or (col in ('numbers', 'wait entries') and len(elems) == 0)):
                            if col == 'numbers':
                                elems.append(DIV('prediction: %d' % (NumberAssignment(shotdb, pid).determine_number()), _id = 'ps_prediction'))

                            elems.append(A('+', _href = URL('crud', args = [table, 'add'], vars = dict(eid = ed['eid'])), _class = 'ps_add_link'))
                            
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
                    mail = mail_conf[idx][2](auth, pid)
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
        
    session.crud = Storage(return_page = 'person_summary', fix_ref_id = dict(person = pid, event = p.events.current.event.id))

    #return dict(form = 1, mailform = 2, name = 3, info = 4, log = 5, data = 6)
    return dict(form = form, mailform = mailform, name = name, info = info, log = log, data = data)

def mail_sent():
    return dict()

@auth.requires_membership('staff')
def number_summary():
    if request.args(0):
        number = int(request.args(0))
        session.selected_number = number
    else:
        number = session.selected_number
    data = None
    
    elems = [SPAN('Sale number: '),
             INPUT(_type = 'text', requires = IS_INT_IN_RANGE(0, 100000, error_message = 'Not an integer!'), _name = 'number', _size = 3),
             INPUT(_type = 'submit', _name = 'submit', _value = 'go!')
            ]
    
    form = FORM(TABLE(TR(*elems)))
    
    if form.validate():
        number = int(form.vars['number'])
        session.selected_number = number
        
    if number:
        eventdata = Numbers(shotdb).number_history(number)
        
        tu = TableUtils()
        data_elements = []
        for d in eventdata:
            if 'person' in d:
                p = d['person'].person
                l = A('%s, %s (%s)' %(p.name, p.forename, p.place), _href = URL('person_summary', args = [p.id]))
            else:
                l = '-'
            data_elements.append(TR(TD(d['label']),
                                    TD(l),
                                    _class = tu.get_class_evenodd()))
        
        data = TABLE(THEAD(TR(TH('Event'), TH('Person'))),
                     TBODY(*data_elements), _class = 'list', _id = 'ps_data_table')
        
    return dict(form = form, number = number, data = data)    

@auth.requires_membership('team')
def number_status_map():
    sef = SimpleEventForm()
    status_map = Numbers(shotdb, sef.event_id).status_map()
    
    # construct table
    width = 10 # number of items in each table row
    rows = []
    row = []
    n_first = 999999
    for item in status_map:
        n, c = item
        if len(row) > 0 and ((n - n_first >= width) or (n % width == 0)):
            rows.append(TR(row))
            row = []
            n_first = n
        row.append(TD(A(str(n), _href = URL('number_summary', args = [n])), _class = c))
        
    if len(row) > 0:
        rows.append(TR(row))
    
    table = TABLE(*rows, _class = 'number_status_map')
    return dict(form = sef.form, table = table)


@auth.requires_membership('team')
def dashboard():
    e = Events(shotdb)
    n = Numbers(shotdb, e.current.event.id)
    w = WaitList(shotdb)
    c = Contributions(shotdb, e.current.event.id)
    
    n_limit = e.current.event.numbers_limit
    if n_limit == None:
        n_limit = 0
    
    return dict(event           = e.current.form_label,
                n_assigned      = n.number_of_assigned(),
                n_wait          = w.length(),
                n_limit         = n_limit,
                n_shifts        = c.get_number_of_shifts(),
                n_donations     = c.get_number_of_donations(),
                wl_status_text  = w.status_text(0),
                shifts          = c.get_shifts(),
                donations       = c.get_donations()
                )


@auth.requires_membership('staff')
def manage_help():
    sef = SimpleEventForm()
    c = Contributions(shotdb, sef.event_id)
    msg_list = c.get_persons_with_message()
    
    # details table
    a_total, t_total = 0, 0
    data_elements = []
    for s in c.get_shifts():
        a, t = s.actual_number, s.target_number
        a_total += a
        if not t:
            t = 0
        t_total += t
        title = A(TABLE(
                    TR(TD('%s, %s:' % (s.day, s.time)), 
                       TD(s.activity, _class = 'mh_activity'),
                       TD('( %d / %d )' % (a, t), _class = getActNumberRatio(a, t)['_class'])
                       ), _class = 'mh_shift_title'), _href = URL('crud/shift/edit', vars = dict(id = s.id)))
        
        data_shift = []
        person_list = []
        for p in c.get_helper_list_for_shift(s.id):
            link = A('%s, %s (%s)' %(p.name, p.forename, p.place), _href = URL('person_summary', args = [p.id]))
            if p.id in msg_list:
                msg = SPAN('msg', _class = 'mh_msg_marker')
            else:
                msg = ''
            person_list.append(SPAN(link, msg))
        
        table_row_list = __row_list(person_list, 2)
        table_row_list.insert(0, A('+', _href = URL('redirect_crud_add/help/%d' % s.id), _class = 'mh_add_link'))
        
        if s.comment:
            data_shift.append(DIV(s.comment, _class = 'mh_comment'))
        
        data_shift.append(DIV(
                                   DIV(SPAN('assigned persons ('), SPAN(' details ', _class = config.cssclass.tggltrig), SPAN('):')),
                                   DIV(TABLE(*table_row_list, _class = 'mh_person_list'),  _class = config.cssclass.tggl)
                                   ))
        
        data_elements.append(TR(DIV(title, DIV(*data_shift, _class = 'mh_shift_body'))))
        
    table = TABLE(*data_elements)
    
    # statistics table
    tu = TableUtils()
    data_stat = []
    data_stat.append((TD('number of shifts'), 
                      TD(SPAN('%d (' % len(data_elements)), A(' + ', _href = URL('crud/shift/add'), _class = 'mh_add_link'), SPAN(')'))
                      ))
    ratio = getActNumberRatio(a_total, t_total)
    data_stat.append((TD('number of assignments'), TD('%d / %d (%d%%)' % (a_total, t_total, ratio['ratio']), _class = ratio['_class'])))
    data_stat.append((TD('number of assigned persons'), TD('%d' % len(c.get_helper_list()))))
    
    table_stat = TABLE(*[TR(*x, _class = tu.get_class_evenodd()) for x in data_stat], _class = 'list')
    
    session.crud = Storage(return_page = 'manage_help', fix_ref_id = dict(event = sef.event_id))
    
    return dict(form = sef.form, table_stat = table_stat, table = table)


@auth.requires_membership('staff')
def manage_donations():
    sef = SimpleEventForm()
    c = Contributions(shotdb, sef.event_id)
    msg_list = c.get_persons_with_message()
    
    # details table
    a_total, t_total, a_total_denied = 0, 0, 0
    data_elements = []

    for d in c.get_donations():
        a, t = d.actual_number, d.target_number
        a_total += a
        t_total += t
        title = A(TABLE(TR(
                       TD(d.item, _class = 'mh_activity'),
                       TD('( %d / %d )' % (a, t), _class = getActNumberRatio(a, t)['_class'])
                       ), _class = 'mh_shift_title'), _href=URL('crud/donation/edit', vars = dict(id = d.id)))
        
        data_donation = []
        
        data_donation.append(DIV(
                                 DIV(SPAN('details ('), SPAN(' toggle ', _class = config.cssclass.tggltrig), SPAN('):')),
                                 DIV(TABLE(__row_list(c.get_notes_list_for_donation(d.id), 3), _class = 'md_notes_list'), BR(),  _class = config.cssclass.tggl)
                                 ))
        
        person_list = []
        person_list_denied = []
        for p in c.get_bringer_list_for_donation(d.id):
            if p.bring.note:
                note = ' (%s)' % p.bring.note
            else:
                note = ''
                
            link = A('%s, %s%s' %(p.person.name, p.person.forename, note), _href = URL('person_summary', args = [p.person.id]))
            if p.person.id in msg_list:
                msg = SPAN('msg', _class = 'mh_msg_marker')
            else:
                msg = ''
            if p.denied:
                person_list_denied.append(SPAN(link, msg))
                a_total_denied += 1
            else:
                person_list.append(SPAN(link, msg))
        
        table_row_list = __row_list(person_list, 2)
        table_row_list.insert(0, A('+', _href = URL('redirect_crud_add/bring/%d' % d.id), _class = 'mh_add_link'))
        
        table_list = [DIV(TABLE(*table_row_list),        _class = 'mh_person_list')]
        if person_list_denied:
            table_row_list_denied = __row_list(person_list_denied, 2)
            table_list.append(DIV(DIV('denied persons (no sale number):'), TABLE(*table_row_list_denied), _class = 'mh_person_list_denied'))
        
        table_row_list_denied = __row_list(person_list_denied, 2)
        
        data_donation.append(DIV(DIV(SPAN('assigned persons ('), SPAN(' toggle ', _class = config.cssclass.tggltrig), SPAN('):')),
                                 DIV(*table_list, _class = config.cssclass.tggl)
                                ))
        
        data_elements.append(TR(DIV(title, DIV(*data_donation, _class = 'mh_shift_body'))))
        
    table = TABLE(*data_elements)
    
    # statistics table
    tu = TableUtils()
    data_stat = []
    data_stat.append((TD('number of donation types'), 
                      TD(SPAN('%d (' % len(data_elements)), A(' + ', _href = URL('crud/donation/add'), _class = 'mh_add_link'), SPAN(')'))
                      ))
    ratio = getActNumberRatio(a_total, t_total)
    a_total_safe = a_total - a_total_denied
    ratio_safe = getActNumberRatio(a_total_safe, t_total)
    data_stat.append((TD('number of individual donations'), TD('%d / %d (%d%%)' % (a_total, t_total, ratio['ratio']), _class = ratio['_class'])))
    data_stat.append((TD('number of safe donations (with sale number)'), TD('%d / %d (%d%%)' % (a_total_safe, t_total, ratio_safe['ratio']), _class = ratio_safe['_class'])))
    data_stat.append((TD('number of assigned persons'), TD('%d' % len(c.get_bringer_list()))))
    
    table_stat = TABLE(*[TR(*x, _class = tu.get_class_evenodd()) for x in data_stat], _class = 'list')
    
    session.crud = Storage(return_page = 'manage_donations', fix_ref_id = dict(event = sef.event_id))
    
    return dict(form = sef.form, table_stat = table_stat, table = table)

def __row_list(elements, n_columns_max):
    '''
    This auxiliary function generates from the list elements a list of table rows in n_colxums_max columns.
    The elements are arranged column after column (not line after line) which is better for sorted data!
    '''
    len_pl = len(elements)
    
    n_columns = max(1, min(n_columns_max, int(len_pl/2)))
    table_row_list = []

    len_col = int((len_pl + n_columns - 1)/n_columns)
    for x in xrange(0, len_col):
        td_data = []
        for i in xrange(0, n_columns):
            idx = x+i*len_col
            if idx < len_pl:
                td_data.append(elements[idx])
        table_row_list.append(TR(*td_data))

    return table_row_list

@auth.requires_membership('staff')
def redirect_crud_add():
    # auxiliary function to transfer the information from the crud link to the session.crud object
    tablename = request.args(0)
    ref_id    = request.args(1)
    
    if tablename == 'help':
        session.crud.fix_ref_id['shift'] = ref_id
    elif tablename == 'bring':
        session.crud.fix_ref_id['donation'] = ref_id
        
    redirect(URL('crud', args = [tablename, 'add']))
    

class SimpleEventForm():
    def __init__(self):
        e = Events(shotdb)
        le = e.get_all_labels_sorted()
        
        name_event  = 'selev'
        
        self.form = FORM(SPAN(T('Event: '),   SELECT(le, _name = name_event, _class = 'autosubmit')))
        
        # extract selections from session object for use in the controller and pre-populate selectors
        # event filter selection
        selev = session.selected_event_simple
        if selev != None:
            self.form.vars[name_event] = selev
            self.event_id = e.all[selev]
        else:
            self.form.vars[name_event] = e.current.form_label
            self.event_id = e.current.event.id 
        
        # process form
        if self.form.process().accepted:
            session.selected_event_simple = self.form.vars[name_event]

            # redirect is necessary to pre-populate the form; didn't find another way
            redirect(request.env.request_uri.split('/')[-1]) 

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
    session.crud = Storage(return_page = 'table/' + t, fix_ref_id = dict(event = f.event_id)) 
    
    return dict(table = t, form = f.form, sqltab = f.sqltab)


@auth.requires_membership('staff')
def crud():
    
    tablename = request.args(0)
    action = request.args(1)
    event_id = request.get_vars['eid']
    record_id = request.get_vars['id']
    
    if session.crud.return_page:
        return_page = URL(session.crud.return_page)
        
    else:
        return_page = URL('table/' + tablename)
        
     
    crud = Crud(shotdb)
    crud.settings.auth = auth   # ensures access control via permissions
    crud.settings.controller = 'staff'
    crud.settings.create_next = return_page
    crud.settings.update_next = return_page
    crud.settings.update_deletable = True
    crud.settings.showid = True

    if session.crud.fix_ref_id:
        for ref_table, ref_id in session.crud.fix_ref_id.iteritems():
            if ref_id > 0 and ref_table in shotdb[tablename]:
                    shotdb[tablename][ref_table].default = ref_id
                    shotdb[tablename][ref_table].writable = False
    
    # add event filter to drop down selectors
    if event_id != None and event_id > 0:
        if tablename == 'help':
            shotdb.help.shift.requires = IS_IN_DB(shotdb(shotdb.shift.event == event_id), 'shift.id', '%(activity)s, %(day)s, %(time)s')
        elif tablename == 'bring':
            shotdb.bring.donation.requires = IS_IN_DB(shotdb(shotdb.donation.event == event_id), 'donation.id', '%(item)s')
    
    if(action == 'add'):            
        crud_response = crud.create(tablename)
    elif(action == 'edit' and record_id != None):
        crud_response = crud.update(tablename, record_id)
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
        le = self.e.get_all_labels_sorted()
        le.insert(0, label_all)
        
        ls = config.colsets[self.tablename]['sets'].keys()
        
        # provide edit links
        shotdb[self.tablename].id.represent = lambda id, row: A(id,_href=URL('crud', args =[self.tablename, 'edit'], vars = dict(id = id)))
        
        # provide links to person summary
        if self.tablename == 'person':
            shotdb[self.tablename].name.represent     = lambda x, row: A(x,_href=URL('person_summary', args = [row.id]))
            shotdb[self.tablename].forename.represent = lambda x, row: A(x,_href=URL('person_summary', args = [row.id]))
        elif 'person' in shotdb[self.tablename]:
            shotdb[self.tablename].person.represent = lambda x, row: A('%s, %s'%(row.person.name, row.person.forename),_href=URL('person_summary', args = [row.person.id]))
        
        formelements = []
        if self.displayeventfilter:
            formelements.append(SPAN(T('event:'),   SELECT(le, _name = name_event, _class = 'autosubmit')))
        formelements.append(SPAN(T('column set:'),  SELECT(ls, _name = name_colset, _class = 'autosubmit')))
        formelements.append(SPAN(INPUT(_type = 'submit', _class = 'button', _value = T('display')), _class = 'js_hide'))
        formelements.append(DIV(BR(), A('Click here to add new entry!', _href=URL('crud', args = [self.tablename, 'add'])), _class = 'link_add_table_element'))
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
                               headers = 'fieldname:capitalize', orderby = 'dummy', _class = 'list',
                               truncate = None)

        