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
from formutils import TableCtrlHead
from gluon.tools import Crud
from benchmark import *
from gluon.storage import Storage
from shotdbutil import Persons




@auth.requires_membership('admin')
def manage_users():

    # retrieve table from session
    if session.manage_users_table_id:
        table_id = session.manage_users_table_id
    else:
        table_id = 'user'

    table_ids = ('user', 'group', 'membership', 'permission', 'event', 'email_type', 'email_subscription')

    formelements = []
    formelements.append(SPAN(T('Auth table:'),  SELECT(table_ids, _name = 'table_id', _class = 'autosubmit')))
    formelements.append(SPAN(INPUT(_type = 'submit', _class = 'button', _value = T('display')), _class = 'js_hide'))
    form = FORM(*formelements, _class = 'admin_ctrl_form')

    form.vars['table_id'] = table_id

    # process form
    if form.process().accepted:
        table_id = form.vars['table_id']
        session.manage_users_table_id = table_id

        # redirect is necessary to pre-populate the form; didn't find another way
        redirect(URL('manage_users'))

    table_name = 'auth_' + table_id
    table_object = shotdb[table_name]

    # queries
    if table_id in ['user', 'group', 'email_type']:
        query = table_object.id > 0

    elif table_id == 'permission':
        query = table_object.group_id == shotdb.auth_group.id

    else:
        query = table_object.user_id  == shotdb.auth_user.id

        if table_id == 'membership':
            query &= table_object.group_id == shotdb.auth_group.id

        elif table_id == 'email_subscription':
            query &= table_object.email_type_id == shotdb.auth_email_type.id

    # provide representations
    table_name = 'auth_' + table_id
    table_object.id.represent = lambda id_, row: A(id_, _href=URL('crud', args = [table_name, 'edit', id_]))

    if 'user_id' in table_object:
        table_object.user_id.represent = lambda x, row: SPAN('%s (%s, %s)'%(row.auth_user.username, row.auth_user.last_name, row.auth_user.first_name))

    if 'group_id' in table_object:
        table_object.group_id.represent = lambda x, row: SPAN('%s'%(row.auth_group.role))

    if 'person' in table_object:
        table_object.person.represent = lambda x, row: A(row.person,_href=URL('staff', 'person_summary', args = [row.person])) if x else ''

    if 'sale_numbers' in table_object:
        table_object.sale_numbers.represent = lambda l, row: SPAN(', '.join([str(n) for n in l]) if l else '')

    # generate table
    if table_id in config.colsets_auth:
        colset = config.colsets_auth[table_id]
    else:
        colset = None

    # get the sorting column from the selected column head
    if request.vars.orderby and session.sort_column:
        if session.sort_column.has_key(table_name) and session.sort_column[table_name] == request.vars.orderby:
            # table is already sorted for this very column => sort in reverse order
            # due to the '~' operator for reverse sorting the database field must be constructed (no better solution so far)
            aux = request.vars.orderby.split('.')
            orderby = ~getattr(getattr(shotdb,aux[-2]),aux[-1])
            del session.sort_column[table_name]
        else:
            # here the string is sufficient
            orderby = request.vars.orderby
            session.sort_column[table_name] = request.vars.orderby
    else:
        orderby = table_object.id
        session.sort_column = {table_name: table_name + '.id'}


    sqltab = SQLTABLE(shotdb(query).select(orderby = orderby),
                               columns = colset,
                               headers = 'fieldname:capitalize', orderby = 'dummy', _class = 'list',
                               truncate = None)

    session.crud = Storage(return_page = URL('admin_', 'manage_users'))


    tabctrl = TableCtrlHead(table_name)

    return dict(form = form, tabctrl = tabctrl, sqltab = sqltab)

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
                    SPAN('(This is necessary after the database has been imported from another site!)')),
                __rectify_wiki),
               (DIV(SPAN('Identify duplicate person entries'),
                    BR(),
                    SPAN('(The person data are scanned for possible duplicates based on name, forename, and place.)')),
                __check_for_duplicate_persons),
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
    slugs = []
    q = shotdb.wiki_page.id > 0
    for page in shotdb(q).select():

        renderer = auth._wiki.get_renderer()
        html = renderer(page)

        # do not spoil wiki tag links with admin_ controller
        html = html.replace('admin_/actions', 'main/wiki')

        shotdb(shotdb.wiki_page.id == page.id).update(html = html)

        slugs.append(page.slug)


    result = DIV(P('The following pages have been rectified:'),BEAUTIFY(slugs))

    return result

def __check_for_duplicate_persons():
    '''
    This function tries to identify duplicate person entries.
    '''
    rows = Persons(shotdb).get_duplicates()
    shotdb.person.name.represent  = lambda x, row: A('%s, %s' % (row.person.name, row.person.forename), _href=URL('staff', 'person_summary', args = [row.person.id]))
    shotdb.person.place.represent = lambda x, row: SPAN('%s, %s %s' % (row.person.place, row.person.street, row.person.house_number))
    sql_table = SQLTABLE(rows,
                    columns = ['person.id', 'person.name', 'person.email', 'person.mail_enabled', 'person.verified', 'person.place', 'person.telephone'],
                    headers = 'fieldname:capitalize', _class = 'list',
                    truncate = None
                    )
    return DIV(P('The following ', STRONG(len(rows)), ' person entries might be duplicates:'), sql_table)



