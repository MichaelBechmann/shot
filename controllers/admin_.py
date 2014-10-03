# Note: Name this file 'admin_' to avoid conflicts with the site administration application! 
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

from shotconfig import config
from gluon.tools import Crud

@auth.requires_membership('admin')
def manage_users():
    
    # retrieve table from session
    if session.manage_users_table_id:
        table_id = session.manage_users_table_id
    else:
        table_id = 'user'
    
    table_ids = ('user', 'group', 'membership', 'permission', 'event')
    
    formelements = []
    formelements.append(SPAN(T('Auth table:'),  SELECT(table_ids, _name = 'table_id', _class = 'autosubmit')))
    formelements.append(SPAN(INPUT(_type = 'submit', _class = 'button', _value = T('display')), _class = 'js_hide'))
    formelements.append(DIV(BR(), A('Click here to add new entry!',_href=URL('crud', args = ['auth_' + table_id, 'add']))))
    form = FORM(*formelements)
    
    form.vars['table_id'] = table_id
    
    # process form
    if form.process().accepted:
        table_id = form.vars['table_id']
        session.manage_users_table_id = table_id
        
        # redirect is necessary to pre-populate the form; didn't find another way
        redirect(request.env.request_uri.split('/')[-1])
    
    # provide edit links
    table = 'auth_' + table_id
    shotdb[table].id.represent = lambda id_, row: A(id_, _href=URL('crud', args = [table, 'edit', id_]))
    
    # generate table
    if table_id in config.colsets_auth:
        colset = config.colsets_auth[table_id]
    else:
        colset = None
    sqltab = SQLTABLE(shotdb(shotdb[table].id > 0).select(),
                               columns = colset,
                               headers = 'fieldname:capitalize', _class = 'list')
    
    return dict(form = form, sqltab = sqltab)

@auth.requires_membership('admin')
def configuration():
    
    # provide edit links
    shotdb.config.id.represent = lambda id_, row: A(id_,_href=URL('crud', args = ['config', 'edit', id_]))
    sqltab = SQLTABLE(shotdb(shotdb.config.id > 0).select(),
                               headers = 'fieldname:capitalize', _class = 'list')
    
    return dict(sqltab = sqltab)


@auth.requires_membership('admin')
def crud():
    tablename = request.args(0)
    action = request.args(1)
    id_ = request.args(2)
    
    return_page = URL(request.env.http_referer.split('/')[-1])
    
    crud = Crud(shotdb)
    crud.settings.controller = 'admin_'
    crud.settings.create_next = return_page
    crud.settings.update_next = return_page
    crud.settings.update_deletable = True
    crud.settings.showid = True   
    
    if(action == 'add'):
        crud_response = crud.create(tablename)
        
    elif(action == 'edit' and id_ != None):
        onaccept = None
        if tablename == 'auth_user':
            shotdb['auth_user']['registration_key'].writable = True
            
        elif tablename == 'config':
            crud.settings.update_deletable = False
            shotdb['config']['name'].writable = False
            
            # update the configuration object, drop the passed argument form
            onaccept = lambda form: config.update(shotdb)

        crud_response = crud.update(tablename, id_, onaccept = onaccept)    
            
    else:
        crud_response = 'Nothing selected!'
    
    return dict(crud_response = crud_response)