# -*- coding: utf-8 -*-
'''
This file contains everything related to the sale data (sale number, contributions, etc.).
'''
# Static analyzer import helpers: (STATIC_IMPORT_MARK)
from _ast import If
if 0:
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb
    global auth

from shotmail import *
from shotdbutil import *
import re
from shoterrors import ShotError
from formutils import regularizeName, ContributionCompleteness, FoundationCheckbox, FormButton, getEnrolmentDataOverview
from urlutils import URLWiki


T.force('de')

def __validateform(form):
    '''
    Functions that take arguments or start with a double underscore are not publicly exposed and can only be called by other functions.
    This validation function checks whether or not at least one of the help shift checkbox fields has been checked.
    Notes on donations are regularized.
    '''

    sale = form.sale
    sale.analyzecheckboxes(form.vars)
    if not (sale.b_does_contribute or sale.b_wants_sale_number):
        form.errors.msg = 'Sie haben angegeben, daß Sie weder eine Kommissionsnummer haben möchten noch helfen oder Kuchen spenden möchten. Bitte wählen Sie etwas aus.'
    elif sale.b_open_contributions_available and not sale.b_does_contribute and not sale.b_cannot_contribute and sale.b_wants_sale_number:
        form.errors.msg = 'Sie haben sich weder für eine Helferschicht noch für eine Kuchenspende eingetragen. Bitte bestätigen Sie, daß Sie nicht helfen können.'
    elif sale.b_does_contribute and sale.b_cannot_contribute:
        form.errors.msg = 'Sie haben widersprüchliche Angaben gemacht. Bitte tragen Sie sich entweder für eine Helferschicht oder einen Kuchen ein oder markieren Sie, daß Sie nicht helfen können.'


    for donation in sale.getdonations():
        if donation.name_note in form.vars:
            form.vars[donation.name_note] = regularizeName(form.vars[donation.name_note])


def form():
    # check whether or not the sale information form shall be displayed
    if session.form_passive:
        # The form shall be displayed for configuration purposes only.
        # Database manipulations are not intended!
        sale = Sale(shift_scope = session.shift_scope)
    elif session.registration_person_id == None:
        # Something went wrong.
        redirect(URLWiki('start'))
        #raise ShotError('Sale form entered without identified person.') # see issue #43
    else:
        # The form is active.
        if session.registration_person_id:
            sale = Sale(session.registration_person_id)
        else:
            raise ShotError('Session object does not contain a valid person id!')

        # Display message in case of overpopulation of shifts or donations
        if session.b_contributions_overpopulation:
            b_contributions_overpopulation = True
            session.b_contributions_overpopulation = False
        else:
            b_contributions_overpopulation = False


    if sale.shift_scope == 'team':
        status_text = 'Als Mitglied des Secondhand-Team Ottersweier erhalten Sie sofort Ihre Nummer.'
    else:
        status_text = WaitList(shotdb).status_text(session.registration_person_id)

    # sale number
    element_sale_number = DIV(DIV(FoundationCheckbox('Ich möchte eine Kommissionsnummer haben.', config.formname.sale_number, value = True),
                                  P('Aktueller Status: ' + status_text),
                                  _class = 'card-section'),
                              _class = 'card',
                              _id = config.cssid.salenumberform)

    # shifts
    shifts_collection = DIV(_class = 'shifts-collection')
    for shift in sale.getshifts():
        status = ContributionCompleteness(shift.actual_number, shift.target_number)

        section = DIV(DIV(shift.timelabel), _class = 'card-section')
        if (not status.complete):
            # display checkbox and comment
            label = 'Ich übernehme diese Helferschicht.'
            if shift.comment:
                toggle_id = shift.name + '-comment'
                section.append(FoundationCheckbox(label, shift.name, toggle_id))
                attributes = {'_id': toggle_id,'_class': 'shift_comment', '_data-toggler': 'is_hidden'}
                section.append(DIV(shift.comment, **attributes))
            else:
                section.append(FoundationCheckbox(label, shift.name))

        card = DIV(DIV(DIV(shift.activity), status.html, _class = 'card-divider'), section, _class = 'card ' + status.display_class)
        shifts_collection.append(card)

    # add dummy elements to fill the last row of the grid => produces equally sized elements
    for i in range(5):
        shifts_collection.append(DIV(_class = 'card flex_last_row_filler'))

    # donations
    donations_collection = DIV(_class = 'donations-collection')
    for donation in sale.getdonations():
        status = ContributionCompleteness(donation.actual_number, donation.target_number)

        card = DIV(DIV(DIV(donation.item), status.html, _class = 'card-divider'), _class = 'card ' + status.display_class)

        if (not status.complete):

            if donation.item == 'Torte':
                article = 'eine'
                name    = 'Name der Torte'

            else:
                article = 'einen'
                name    = 'Name des Kuchens'

            label = 'Ich spende %s %s.' % (article, donation.item)

            if (donation.enable_notes):
                toggle_id = donation.name + '-comment'
                section = DIV(FoundationCheckbox(label, donation.name, toggle_id), _class = 'card-section')
                attributes = {'_id': toggle_id,'_class': 'donation_note', '_data-toggler': 'is_hidden'}
                section.append(DIV(DIV('Um etwas Vielfalt an der Kuchentheke zu gewährleisten, können Sie hier eintragen, was genau Sie bringen werden (bitte keine Tiefkühlware):'),
                               INPUT(_type = 'text', _name = donation.name_note, _placeholder = name),
                               DIV('Andere bringen dies:'),
                               UL(*map(LI,donation.notes)),
                               **attributes
                               ))
            else:
                section = DIV(FoundationCheckbox(label, donation.name), _class = 'card-section')

            card.append(section)
        donations_collection.append(card)

    # add dummy elements to fill the last row of the grid => produces equally sized elements
    for i in range(5):
        donations_collection.append(DIV(_class = 'card flex_last_row_filler'))

    # construct the form
    formelements = [H2('Kommissionsnummer'),      element_sale_number,
                    H2('Helferschichten'),        shifts_collection,
                    H2('Spenden für unser Café'), donations_collection]

    # add check box 'I cannot help'; display only if there are still open shifts or donations to choose from
    if sale.b_open_contributions_available:
        element_cannot_contribute = DIV(FoundationCheckbox('Ich kann weder eine Helferschicht übernehmen noch einen Kuchen / Waffelteig für das Café spenden.', config.formname.no_contrib),
                                        _id = config.cssid.nocontrib)
        formelements.extend([H2('Sie können nicht helfen?'), element_cannot_contribute])

    # add message box and send button
    message_box = DIV(DIV(TEXTAREA(_type = 'text', _name = config.formname.person_message, _rows = 3,
                                   _placeholder = 'Wenn Sie möchten, können Sie hier noch eine Nachricht an uns beifügen.'),
                                   _class = 'medium-12'),
                      _class = 'grid-x grid-padding-x')
    formelements.extend([H2('Haben Sie Fragen oder Anmerkungen?'), message_box, FormButton().next()])

    form = FORM(*formelements)

    if session.form_passive:
        if 'submit next' in request.vars:
            session.form_passive = None
            session.sale_vars = None
            redirect(URL('config', 'config_event'))
    else:
        # pre-populate the form in case of re-direction from confirmation page (back button pressed)
        # see book, section 'Pre-populating the form' in chapter 'Forms and Validators'
        if session.sale_vars:
            form.vars = session.sale_vars

        form.sale = sale
        if form.validate(onvalidation = __validateform):
            session.sale_vars = form.vars
            redirect(URL('confirm'))

        response.flash_custom_display = True # hide default wiki flash messages

    return dict(announcement = sale.announcement, form = form, b_contributions_overpopulation = b_contributions_overpopulation)


def confirm():
    # check if there is personal information to be confirmed
    if (session.sale_vars == None) or (session.registration_person_id == None):
        redirect(URLWiki('start'))
    sale = Sale(session.registration_person_id)

    sale.analyzecheckboxes(session.sale_vars)

    # Redirect back to form in case one or more selected contributions are not available anymore.
    list_overpopulated_contributions = sale.getContributionsOverpopulation()
    if list_overpopulated_contributions:
        for cid in list_overpopulated_contributions:
            # The form variables must be deleted. Otherwise the redirected page will initialize non-existing input fields which will then remain forever!
            del session.sale_vars[cid]
        session.b_contributions_overpopulation = True
        redirect(URL('form'))

    # construct a list of all data to be confirmed
    dataelements = []

    # person
    dataelements.append(['Ich bin:', STRONG(sale.person_name)])

    # sale number
    if sale.b_wants_sale_number:
        msg = DIV('Ich möchte eine Kommissionsnummer haben für den %s.' % sale.announcement)
        if sale.b_cannot_contribute and not sale.b_is_team_member:
            msg.append(BR())
            msg.append('(Hinweis: %s)' % WaitList(shotdb).status_text(session.registration_person_id))
    else:
        msg = DIV('Ich möchte ', STRONG('keine'), ' Kommissionsnummer haben.')
    dataelements.append(['Kommissinsnummer:', msg])

    # shifts
    if sale.b_does_help:
        for s in sale.getcheckedshifts():
            msg = DIV(s.day + ', ' + s.time + ', ' + s.activity)
            if(s.comment != None and s.comment != ''):
                msg.append(BR())
                msg.append('(%s)' % s.comment)
            dataelements.append(['Hier helfe ich:', msg])
            dataelements.append(['', auth.get_shotwiki_page(slug_base = 'email-snippet-helper-general-text')])
    else:
        dataelements.append(['Helferschichten:', 'Ich übernehme keine Helferschicht.'])

    # donations
    if sale.b_does_donate:
        for d in sale.getcheckeddonations():
            out = d.item
            if d.note != None:
                out += ' (' + d.note + ')'
            dataelements.append(['Das bringe ich mit:', out])
    else:
        dataelements.append(['Kuchenspenden:', 'Ich bringe für das Café nichts mit.'])

    # message
    if session.sale_vars[config.formname.person_message]:
        dataelements.append(['Meine Nachricht:', session.sale_vars[config.formname.person_message]])


    data = getEnrolmentDataOverview(dataelements)

    form = FORM(DIV(
                    FormButton().back(),
                    FormButton().send('Anmeldung absenden'),
                    _class = 'expanded button-group'
                    )
                )

    data.append(form)

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

    return(dict(data = data))

def final():
    return dict()

def final_wait():
    return dict()

class Sale():
    '''
    This class provides methods for handling all sale related information like sale numbers or help information.
    These methods include all interaction with the database.

    argument: pid - person id
    '''
    def __init__(self, pid = 0, shift_scope = None):
        self.pid = pid
        if self.pid == 0:
            self.shift_scope = shift_scope
            if self.shift_scope == 'team':
                self.b_is_team_member = True
            else:
                self.b_is_team_member = False
        else:
            # determine whether or not the person is a team member
            self.b_is_team_member = Team(shotdb).IsMember(pid)
            if self.b_is_team_member:
                self.shift_scope = 'team'
            else:
                self.shift_scope = 'public'

        e = Events(shotdb)
        self.announcement    = e.get_current_announcement(b_include_time = False)
        self.currentevent_id = e.current.event.id

        self.contrib = Contributions(shotdb, self.currentevent_id)
        self.b_open_shifts_available        = self.contrib.get_number_of_shifts(self.shift_scope)['open'] > 0
        self.b_open_donations_available     = self.contrib.get_number_of_donations()['open'] > 0
        self.b_open_contributions_available = self.b_open_shifts_available  or self.b_open_donations_available

        self.person_name = 'anonymous'

        rows = shotdb(shotdb.person.id == self.pid).select()
        if len(rows) > 0:
            person = rows.last()
            # get name of the person
            self.person_name = person.forename + ' ' + person.name

    def _getFormNameShift(self, row):
        # format: configured marker name '§' database id
        return config.formname.shift + '§' + str(row.id)

    def _getFormNameDonation(self, row):
        # format: configured marker name '§' database id
        return config.formname.donation + '§' + str(row.id)

    def _getFormNameNote(self, row):
        # format: configured marker name '§' database id
        return config.formname.note + '§' + str(row.id)


    def getshifts(self):
        '''
        This function retrieves all shifts belonging to the current event and adds some evaluated properties.
        '''
        rows = self.contrib.get_shifts(scope = self.shift_scope)
        for r in rows:
            r.timelabel = r.day + ', ' + r.time
            r.label     = r.day + ', ' + r.time + ', ' + r.activity
            r.name      = self._getFormNameShift(r)

        # Note: Here a reference is returned!
        return rows

    def getdonations(self):
        '''
        This function retrieves all donations belonging to the current event and adds some evaluated properties.
        '''
        rows = self.contrib.get_donations()
        for r in rows:
            r.label     = r.item
            r.name      = self._getFormNameDonation(r)
            r.name_note = self._getFormNameNote(r)
            r.notes     = self.contrib.get_notes_list_for_donation(r.id)

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
        self.shifts_checked    = []
        self.donations_checked = {}
        self.b_does_help       = False
        self.b_does_donate     = False
        # iterate through the dictionary 'vars' containing the form elements
        # for the form elements which have been checked => decode the database table and the id from the key
        p = re.compile('^([a-z]+)§([0-9]+)$')
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
                        self.b_does_donate = True
        self.b_does_contribute = self.b_does_help or self.b_does_donate

        p = re.compile('^{n}§([0-9]+)$'.format(n = config.formname.note))
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

        self.b_cannot_contribute = self.vars[config.formname.no_contrib] == 'on'

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

    def getContributionsOverpopulation(self):
        '''
        This method returns a list with all form names which correspond to over-populated contributions.
        '''
        l = []
        for shift in self.getcheckedshifts():
            if shift.actual_number >= shift.target_number:
                l.append(self._getFormNameShift(shift))

        for donation in self.getcheckeddonations():
            if donation.actual_number >= donation.target_number:
                l.append(self._getFormNameDonation(donation))

        return l


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
            shotdb.message.update_or_insert(event = self.currentevent_id, person = self.pid, text = self.vars[config.formname.person_message])


        # sale numbers
        self.b_sale_number_assigned = False
        if self.b_wants_sale_number:
            # set person on wait list
            shotdb.wait.update_or_insert(event = self.currentevent_id, person = self.pid)
            if (self.b_does_contribute or self.b_is_team_member):
                # person gets sale number immediately
                if NumberAssignment(shotdb, self.pid).assign_number() > 0:
                    # sale number has been assigned successfully or person already has a sale number
                    shotdb.commit()
                    NumberMail(auth, self.pid).send()
                    self.b_sale_number_assigned = True

            if self.b_sale_number_assigned == False:
                # person shall not be assigned a sale number or assignment failed (no free numbers left)
                # send wait list mail
                shotdb.commit()
                WaitMail(auth, self.pid).send()
        else:
            shotdb.commit()
            NumberMail(auth, self.pid).send()
