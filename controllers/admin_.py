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
from benchmark import *
from gluon.storage import Storage

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
                               headers = 'fieldname:capitalize', _class = 'list',
                               truncate = None)
    
    session.crud = Storage(return_page = URL('admin_', 'manage_users'))
    
    return dict(form = form, sqltab = sqltab)

@auth.requires_membership('admin')
def configuration():
    
    # provide edit links
    shotdb.config.id.represent = lambda id_, row: A(id_,_href=URL('crud', args = ['config', 'edit', id_]))
    sqltab = SQLTABLE(shotdb(shotdb.config.id > 0).select(),
                               headers = 'fieldname:capitalize', _class = 'list',
                               truncate = None)
    
    session.crud = Storage(return_page = URL('admin_', 'configuration'))
    
    return dict(sqltab = sqltab)


@auth.requires_membership('admin')
def crud():
    tablename = request.args(0)
    action = request.args(1)
    id_ = request.args(2)
    
    if session.crud and session.crud.return_page:
        return_page = session.crud.return_page
    else:
        return_page = URL('admin_', 'manage_users')
    
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


@auth.requires_membership('admin')
def benchmark():
    
    l = [BenchmarkCalculations().run(),
         BenchmarkListManipulation().run(),
         BenchmarkHTMLHelper().run(),
         BenchmarkDBQuery(shotdb).run(),
         #BenchmarkSleep().run(),
        ]
    
    total = 0
    for r in l:
        total += r['duration']
    
    rl = []
    for r in l:
        d = r['duration']
        rl.append(TR(r['id'], '%.1f sec' % d, '%.1f %%' % (d/total * 100)))
        
    rl.append(TR('Total duration', '%.1f sec' % total, '100 %'))
    
    return dict(results = TABLE(*rl, _class = 'list'))
    
    
@auth.requires_membership('admin')
def actions():
    result = None
    
    actions = ((DIV(SPAN('Rectify wiki links'), 
                    BR(), 
                    SPAN('(Necessary after the database has been imported from another site!)')),
                __rectify_wiki),
              )
    
    rows = [TR(actions[i][0],
               INPUT(_type = 'submit', _name = str(i), _value = 'go!', _class = "irreversible")
               ) for i in range(len(actions))]
    form = FORM(TABLE(*rows, _class = 'caution'))
    
    for k in request.vars.iterkeys():
        f = actions[int(k)][1]
        result = f()
        break
    
    return dict(form = form, result = result)


def __rectify_wiki():
    '''
    This function loops through all rows of table wiki_page. For each page the body is retrieved and then converted to html which is then stored in the database.
    This is necessary to fix all links all copying the database from some other site.
    '''
    auth.shotwiki()
    slugs = []
    q = shotdb.wiki_page.id > 0
    for page in shotdb(q).select():
        
        renderer = auth._wiki.get_renderer()
        shotdb(shotdb.wiki_page.id == page.id).update(html = renderer(page))
        
        slugs.append(page.slug)
    
    
    result = DIV(P('The following pages have been rectified:'),BEAUTIFY(slugs))
    
    return result


