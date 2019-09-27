# -*- coding: utf-8 -*-
'''
creation: bechmann, Nov 21, 2013

This module contains all controller functions related to the appropriation requests.
'''

# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0:
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb
    global auth
    global T

from shotconfig import *
from formutils import *
from shotdbutil import PersonEntry, AppropriationRequestEntry
from shotmail import AppropriationRequestMail
from urlutils import URLWiki
import subprocess

T.force('de')

def __regularize_form_input(form):
    '''
    This function brings the user input to standard.
    '''
    # check fields from table person
    regularizeFormInputPersonForm(form)

    # check fields from table request
    for field in ('project', 'organization'):
        form.vars[field] = regularizeName(form.vars[field])


def form():
    # note: multiple tables in SQLFORM must not have identical field names, see http://web2py.com/books/default/chapter/29/7#One-form-for-multiple-tables
    display_fields = ['project', 'organization', 'forename', 'name', 'place', 'zip_code', 'street', 'house_number', 'telephone', 'email', 'amount_total', 'amount_requested', 'description', 'data_use_agreed']

    shotdb.person.data_use_agreed.widget = lambda field, value: FoundationWidgetFieldsetSingleCheckbox(field, value, config.data_use_agreed_option['appropriation'])

    form = SQLFORM.factory(shotdb.person,
                           shotdb.request,
                           fields = display_fields,
                           formstyle= generateFoundationForm,
                           buttons = [FormButton().next()], _id = 'form_request')



    if session.appropriation_request:
        # pre-populate the form in case of re-direction from confirmation page (back button pressed)
        # see book, section 'Pre-populating the form' in chapter 'Forms and Validators'
        form.vars = session.appropriation_request


    explanations = (( 0, DIV(H2('Allgemeines'),
                             P('Welcher Verein, welche Institution oder Einrichtung organisiert dieses Projekt? Sollte nichts zutreffen, tragen Sie bitte "privat" ein.'))),
                    ( 3, DIV(H2('Anspechpartner'),
                             P('Bitte geben Sie die persönlichen Daten einer Kontaktperson an, über die wir wenn nötig weitere Informationen über Ihr Projekt erhalten können.'))),
                    (12, DIV(H2('Kosten'),
                             P('Bitte teilen Sie uns mit, wie groß der finanzielle Bedarf Ihres Projektes insgesamt ist und welchen Anteil Sie davon als Fördermittel beantragen möchten.'))),
                    (15, DIV(H2('Projektbeschreibung'),
                             P('''Natürlich interessiert uns besonders, wie die beantragten Fördermittel eingesetzt werden sollen.
                                  Bitte nehmen Sie sich also etwas Zeit, Ihr Projekt möglichst genau zu beschreiben und Ihren Antrag zu begründen.
                                  Wer soll gefördert werden, also welche und wieviele Kinder, Jugendliche oder Familien?
                                  Wenn möglich, definieren Sie bitte auch den zeitlichen Rahmen Ihres Projektes, also etwa das Datum einer Veranstaltung oder Beginn und Dauer der zu fördernden Aktivitäten.
                                '''))),
                    (17, DIV(H2('Datenschutz'),
                             P(SPAN('''Um Ihren Antrag verarbeiten zu können, benötigen wir Ihre Einwilligung, Ihre hier angegebenen Daten zu speichern und zu verarbeiten.
                                  Genaue Informationen dazu finden Sie in unserer '''), A('Datenschutzerklärung', _href = URLWiki('dataprivacy'), _class="intext", _target="_blank"), SPAN('.'))))
                    )
    for e in explanations:
        form[0].insert(e[0], TR(TD(e[1], _colspan = 3)))

    # There is a mistake in the book: form.validate() returns True or False. form.process() returns the form itself
    # see http://osdir.com/ml/web2py/2011-11/msg00467.html
    if form.validate(onvalidation = __regularize_form_input):
        session.appropriation_request = form.vars
        redirect(URL('appropriation','confirm'))

    return dict(form=form)


def confirm():
    # check if there is personal information to be confirmed
    if session.appropriation_request == None:
        redirect(URLWiki('start'))

    data_person = getPersonDataOverview(session.appropriation_request, type = 'appropriation')
    data_project = getAppRequestDataOverview(session.appropriation_request)

    form = FORM(DIV(
                    FormButton().back(),
                    FormButton().send('Antrag senden'),
                    _class = 'expanded button-group'
                    )
                )

    data_project.append(form)

    if 'submit back' in request.vars:
        redirect(URL('form'))

    elif 'submit send' in request.vars:
        pe = PersonEntry(shotdb, session.appropriation_request)

        if (pe.exists):
            # The person is known already.
            pe.update()

        else:
            # person is not known yet.
            pe.insert()

        ar = AppropriationRequestEntry(shotdb, session.appropriation_request, pe.id)

        # clear request data
        session.appropriation_request = None

        # send email to person who submitted the request
        shotdb.commit()
        AppropriationRequestMail(auth, ar.aid).send()

        # send email to team members
        script_path = 'applications/%s/%s' % (config.appname, 'background/mail/send_team_info_new_request.py')
        args = ['python', 'web2py.py', '-S', config.appname , '-M', '-R', script_path, '-A']
        args.extend([str(ar.aid)])
        subprocess.Popen(args)

        redirect(URLWiki('appropriation-final'))

    return(dict(data_person = data_person, data_project = data_project))

