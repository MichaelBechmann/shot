# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0:
    from gluon import *
    from gluon.languages import translator as T
    global request
    global response
    global session
    global shotdb
    global auth

from gluon.tools import Crud
from shotdbutil import Events, CopyConfig
from formutils import *


@auth.requires_membership('configurator')
def crud():
    tablename = request.args(0)
    action = request.args(1)
    record_id = request.get_vars['id']
    
    crud_ = Crud(shotdb)
    crud_.settings.controller  = 'config'
    crud_.settings.create_next = URL('config_event')
    crud_.settings.update_next = URL('config_event')
    crud_.settings.update_deletable = False
    crud_.settings.showid = True  
    
    if(action == 'add'):            
        crud_response = crud_.create(tablename)
    elif(action == 'edit' and record_id != None):
        crud_response = crud_.update(tablename, record_id)
    else:
        crud_response = 'Nothing selected!'
    
    return dict(crud_response = crud_response)


@auth.requires_membership('configurator')
def config_event():
    
    if 'submit_view_form' in request.vars:
        session.form_passive = True
        redirect(URL('sale', 'form'))
    
    
    event_obj = Events(shotdb)
    
    # The _name arguments are important as the one of the pressed button will appear in request.vars.
    button_view_form = FORM(INPUT(_type = 'submit', _class = 'button', _name = 'submit_view_form', _value = T('view form')))
    
    # provide edit links
    shotdb[shotdb.event_type].id.represent = lambda id, row: A(id,_href = URL('crud', args =['event_type', 'edit'], vars = dict(id = id)))
    
    table_event_types = SQLTABLE(shotdb(shotdb.event_type.id > 0).select(),
                                 headers='fieldname:capitalize',
                                 _class = 'list')
    tabctrl_event_types = TableCtrlHead('event_type', sorttext = None)


    # construct the config events main table
    table_heads = [TH(x) for x in ('Id', 'Label', 'Type', 'Date', 'Time', 'Enrol date', 'Active', 'Visible')]
    table_heads.append(TH(SPAN('exp.', _class = 'cexpand'), SPAN(' / '), SPAN('col.    ', _class = 'ccollapse')))
    event_rows = [THEAD(TR(*table_heads))]
    tu = TableUtils()
    for event in event_obj.get_complete_table().sort(lambda event: -event.event.id):
        e = event.event
        id_ = e.id
        row_class = tu.get_class_evenodd()
        
        main_row = TR(A(id_, _href = URL('crud', args = ['event', 'edit'], vars = dict(id = id_))),
                        e.label, event.event_type.label, e.date, e.time, e.enrol_date, e.active, e.visible, TD('details', _class = config.cssclass.tggltrig),
                        _class = 'event_main_row ' + row_class)
        
        sub_row = TR(TD(*[SPAN(SPAN('%s: ' % x[0], _class = 'field'), SPAN(x[1], _class = 'value')) for x in 
                          [('template set', e.template_set), ('number ranges', e.number_ranges), ('numbers limit', e.numbers_limit), ('email bring request', e.email_bring_request)]],
                        _colspan = '9'), _class = 'event_sub_row ' + row_class + ' ' + config.cssclass.tggl)
        
        event_rows.extend([main_row, sub_row])
        
    table_events = TABLE(event_rows, _class = 'list')
    tabctrl_events = TableCtrlHead('event', sorttext = None)

    # form to copy event canfiguration
    le = event_obj.get_all_labels_sorted()
    le.insert(0, ' Please select ...')
    
    copy_form = FORM(TABLE(TR('Source Event: ', SELECT(le, _name = 'event'),
                                    INPUT(_type = 'submit', _class = 'button', _name = 'submit_copy', _value = T('copy configuration')))))  
        
    if copy_form.process().accepted:
        selev = copy_form.vars['event']
        if selev not in event_obj.all:    
            response.flash = 'Please select a source event!'
        else:
            cc = CopyConfig(shotdb, event_obj.all[selev])
            
            # copy shifts
            n_s = cc.copy_shifts()
            
            # copy donations
            n_d = cc.copy_donations()
            
            response.flash = 'Inserted or updated %d shifts and %d donations.' % (n_s, n_d)


    return dict(table_event_types   = table_event_types,
                table_events        = table_events,
                tabctrl_event_types = tabctrl_event_types,
                tabctrl_events      = tabctrl_events,
                button_view_form    = button_view_form,
                copy_form           = copy_form)
    