from datetime import date, datetime, timezone

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Value
from django.db.models.functions import Concat
from django.utils.html import escape

import deqarclient.agency
from deqarclient.api import EqarApi
from deqarclient.errors import HttpError

from agencies.models import RegisteredAgency
from contacts.models import Contact, ContactOrganisation

import phonenumbers

import json

class RemoteAgency(deqarclient.agency.Agency):

    def __init__(self, api, pk, command):
        self.command = command
        self.name_primary = None
        self.acronym_primary = None
        self.is_changed = False
        super().__init__(api, pk)

    def update(self, local):
        self.update_address(local)
        self.update_contact_names(local)
        self.update_contact_emails(local)
        self.update_contact_phones(local)

    def update_address(self, local):
        # postal address
        local_address = '<p>' + \
            '<br>'.join([ escape(line) for line in [
                local.instance.organisation.address1,
                local.instance.organisation.address2,
                f'{local.instance.organisation.postcode} {local.instance.organisation.city}',
            ] if line ]) + \
            '</p>'
        if self.data['address'] != local_address:
            self.command.stdout.write(self.command.style.SUCCESS(f'  > address: {"; ".join(self.data["address"].splitlines())} -> {"; ".join(local_address.splitlines())}'))
            self.data['address'] = local_address
            self.is_changed = True
        # country
        local_country = self.api.Countries.get(local.instance.organisation.country.iso3)
        if self.data['country'] != local_country['id']:
            self.command.stdout.write(self.command.style.SUCCESS(f'  > country: {self.api.Countries.get(self.data["country"])["name_english"]} -> {local_country["name_english"]}'))
            self.data['country'] = local_country['id']
            self.is_changed = True

    def normalize_phone(self, phone):
        try:
            parsed = phonenumbers.parse(phone, 'BE')
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except phonenumbers.phonenumberutil.NumberParseException:
            return phone

    def update_contact_names(self, local):
        # contact person name(s)
        contact_person = ', '.join([ i['contact__person'] for i in local.instance.organisation.contactorganisation_set.filter(nameOnRegister=True).order_by('contact__person').values('contact__person') ]) or 'not applicable'
        if self.data['contact_person'] != contact_person:
            self.command.stdout.write(self.command.style.SUCCESS(f"  > contact: {self.data['contact_person']} -> {contact_person}"))
            self.data['contact_person'] = contact_person
            self.is_changed = True

    def update_contact_emails(self, local):
        # emails
        remote_emails = { i['email']: i for i in self.data['emails'] }
        local_emails = { i['contact__email'] for i in local.instance.organisation.contactorganisation_set.filter(emailOnRegister=True).values('contact__email') if i['contact__email'] }
        for email in list(remote_emails): # list() needed b/c we cannot change the set while iterating over itself
            if email not in local_emails:
                self.command.stdout.write(self.command.style.WARNING(f"  > - {email}"))
                del remote_emails[email]
        for email in local_emails:
            if email not in remote_emails:
                remote_emails[email] = { 'email': email }
                self.command.stdout.write(self.command.style.SUCCESS(f"  > + {email}"))
        if self.data["emails"] != list(remote_emails.values()):
            self.data["emails"] = list(remote_emails.values())
            self.is_changed = True

    def update_contact_phones(self, local):
        # phone number(s)
        remote_phones = { self.normalize_phone(i['phone']): i for i in self.data['phone_numbers'] }
        local_phones = { i['contact__phone'] for i in local.instance.organisation.contactorganisation_set.filter(phoneOnRegister=True).values('contact__phone') if i['contact__phone'] }
        for phone in list(remote_phones):
            if phone not in local_phones:
                self.command.stdout.write(self.command.style.WARNING(f"  > - {phone}"))
                del remote_phones[phone]
        for phone in local_phones:
            if phone not in remote_phones:
                remote_phones[phone] = { 'phone': phone }
                self.command.stdout.write(self.command.style.SUCCESS(f"  > + {phone}"))
        if self.data["phone_numbers"] != list(remote_phones.values()):
            self.data["phone_numbers"] = list(remote_phones.values())
            self.is_changed = True

    def save_if_changed(self):
        if self.is_changed:
            self.command.stdout.write(self.command.style.SUCCESS(f'  > saving remote: {self.acronym_primary}'))
            try:
                self.save(comment='synchronised by EQAR-DB')
            except:
                self.command.stdout.write(json.dumps(self.data))
                raise
            self.is_changed = False
        else:
            self.command.stdout.write(f'  = remote {self.acronym_primary} unchanged')


class LocalObject:

    def __init__(self, instance, command):
        self.instance = instance
        self.command = command
        self.is_changed = False

    def update_property(self, prop, remote_value):
        """
        Updates local object's attribute to value remote, if different
        """
        if getattr(self.instance, prop) != remote_value:
            self.command.stdout.write(self.command.style.SUCCESS(f'  < {prop}: {getattr(self.instance, prop)} -> {remote_value}'))
            setattr(self.instance, prop, remote_value)
            self.is_changed = True

    def parse_remote_date(self, remote_value):
        if remote_value:
            return date.fromisoformat(remote_value)
        else:
            return None

    def save_if_changed(self):
        if self.is_changed:
            self.command.stdout.write(self.command.style.SUCCESS(f'  < saving local: {self.instance}'))
            self.instance.save()
            self.is_changed = False
        else:
            self.command.stdout.write(f'  = local {self.instance} unchanged')

class LocalAgency(LocalObject):

    def update(self, remote):
        self.update_property('registered', remote.data['is_registered'])
        self.update_property('registeredSince', self.parse_remote_date(remote.data['registration_start']))
        self.update_property('validUntil', self.parse_remote_date(remote.data['registration_valid_to']))
        self.update_property('shortname', remote.acronym_primary)

class LocalOrganisation(LocalObject):

    def update(self, remote):
        self.update_property('acronym', remote.acronym_primary)
        self.update_property('longname', remote.name_primary)


class AgencySyncer:

    def __init__(self, api, local, command):
        self.command = command
        self.local = LocalAgency(local, command)
        self.local_organisation = LocalOrganisation(local.organisation, command)
        self.remote = RemoteAgency(api, local.deqarId, command)

    def sync(self):
        self.command.stdout.write(f'- Syncing {self.remote.acronym_primary} (deqar_id={self.remote.id} <-> local_pk={self.local.instance.id}):')
        if self.remote.acronym_primary != self.local.instance.shortname:
            self.command.stdout.write(self.command.style.NOTICE(f'  ! acronyms mismatch: remote={self.remote.acronym_primary} != local={self.local.instance.shortname}'))
        self.local.update(self.remote)
        self.local_organisation.update(self.remote)
        self.remote.update(self.local)

    def commit(self):
        self.local.save_if_changed()
        self.local_organisation.save_if_changed()
        self.remote.save_if_changed()


class Command(BaseCommand):
    help = 'Synchronise data on registered agencies with DEQAR'

    def add_arguments(self, parser):
        parser.add_argument('agency_id', nargs='*', type=int,
                            help = 'only synchronise selected agency IDs')
        parser.add_argument("-b", "--base",
                            help="Base URL to the DEQAR admin API (default: DEQAR_BASE from settings.py)")
        parser.add_argument("-t", "--token",
                            help="DEQAR API token (default: DEQAR_TOKEN from settings.py)")
        parser.add_argument('-n', '--dry-run', action='store_true',
                            help = 'check differences and only tell what would be synchronised')

    def handle(self, *args, **options):

        try:
            api = EqarApi(options['base'] or settings.DEQAR_BASE, token=(options['token'] or settings.DEQAR_TOKEN), request_timeout=600)
        except:
            raise CommandError('Error connecting to DEQAR API.')

        agencies = RegisteredAgency.objects.exclude(deqarId__isnull=True)
        if options['agency_id']:
            agencies = agencies.filter(id__in=options['agency_id'])

        for agency in agencies:
            try:
                syncer = AgencySyncer(api, agency, self)
            except HttpError:
                self.stdout.write(self.style.NOTICE(f'- failed to retrieve agency id={agency.deqarId}, skipped.'))
            else:
                syncer.sync()
                if not options['dry_run']:
                    syncer.commit()

