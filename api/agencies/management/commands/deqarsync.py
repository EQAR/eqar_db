from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Value
from django.db.models.functions import Concat

from agencies.deqarclient import EqarApi
from agencies.models import RegisteredAgency
from contacts.models import Contact


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

    def sync_property(self, remote, local_object, attribute, commit=False):
        """
        Updates local_object's attribute to value remote, if different, and saves local_object to database.
        """
        if local_object is not None and hasattr(local_object, attribute) and getattr(local_object, attribute) != remote:
            self.stdout.write(self.style.SUCCESS('  * update {}: {} -> {}'.format(attribute, getattr(local_object, attribute), remote)))
            if commit:
                setattr(local_object, attribute, remote)
                local_object.save()
            return True
        else:
            return False

    def sync_contact(self, remote, local, commit=False):
        """
        Checks if contact person is known by email or name, and updates web_contact on local accordingly. If contact is not found, it is created.
        """
        contact = None

        # first try is by email address, and we use whichever matches first:
        for email in remote['emails']:
            try:
                contact = Contact.objects.get(email=email['email'])
            except Contact.DoesNotExist:
                pass
            else:
                break

        # if not found, we will try by name instead:
        if contact is None:
            matches = Contact.objects.annotate(name_search=Concat('firstName', Value(' '), 'lastName')).filter(name_search=remote['contact_person'], organisation=local.organisation)
            if len(matches) > 0:
                contact = matches[0]
            else:
                # if that didn't work either AND we do have an email address, we create a new contact:
                if remote['emails']:
                    contact = Contact(
                        firstName=remote['contact_person'].split(' ')[0],
                        lastName=' '.join(remote['contact_person'].split(' ')[1:]),
                        email=remote['emails'][0]['email']
                    )
                    self.stdout.write(self.style.WARNING('  * created contact: {}'.format(contact)))
                    if commit:
                        contact.save()
                        contact.organisation.add(local.organisation)
                        contact.contactorganisation_set.update(function='[website contact added by sync]')

        # finally, we update the web_contact field if the contact we found/created differs
        if contact is not None and contact != local.web_contact:
            self.stdout.write(self.style.SUCCESS('  * update web_contact: {} -> {}'.format(local.web_contact, contact)))
            if commit:
                local.web_contact = contact
                local.save()
            return True
        else:
            return False

    def handle(self, *args, **options):

        try:
            api = EqarApi(options['base'] or settings.DEQAR_BASE, options['token'] or settings.DEQAR_TOKEN)

        except:
            raise CommandError('Error connecting to DEQAR API.')

        if options['agency_id']:
            agencies = options['agency_id']
        else:
            agencies = [ agency['id'] for agency in api.get('/adminapi/v1/browse/all/agencies/', kwargs=dict(limit=100))['results'] ]

        for remote_id in agencies:

            try:
                remote = api.get('/adminapi/v1/agencies/{}/'.format(remote_id))
            except:
                self.stdout.write(self.style.NOTICE('- failed to retrieve agency id={}, skipped.'.format(remote_id)))

            try:
                local = RegisteredAgency.objects.get(deqar_id=remote['id'])
            except Agency.DoesNotExist:
                self.stdout.write('{acronym_primary} not found with deqar_id={id}'.format(**remote))
            else:
                self.stdout.write('- Syncing {} (deqar_id={} / local_pk={}):'.format(remote['acronym_primary'], remote['id'], local.id))

                any_changes = False

                any_changes |= self.sync_property(remote['acronym_primary'],                            local,              'shortname',            commit=(not options['dry_run']))
                any_changes |= self.sync_property(remote['acronym_primary'],                            local.organisation, 'acronym',              commit=(not options['dry_run']))
                any_changes |= self.sync_property(remote['name_primary'],                               local.organisation, 'longname',             commit=(not options['dry_run']))
                any_changes |= self.sync_property(date.fromisoformat(remote['registration_start']),     local,              'registered_since',     commit=(not options['dry_run']))
                any_changes |= self.sync_property(date.fromisoformat(remote['registration_valid_to']),  local,              'valid_until',          commit=(not options['dry_run']))
                any_changes |= self.sync_property(remote['country']['iso_3166_alpha3'],                 local,              'base_country_id',      commit=(not options['dry_run']))
                any_changes |= self.sync_contact(remote,                                                local,                                      commit=(not options['dry_run']))

                if not any_changes:
                    self.stdout.write('  = unchanged')

        self.stdout.write(self.style.WARNING('\nAgencies not synchronised:'))

        for agency in RegisteredAgency.objects.exclude(deqar_id__in=agencies):
            self.stdout.write("- {} (deqar_id={})".format(agency, agency.deqar_id or 'NULL'))

        self.stdout.write(self.style.SUCCESS('\nDone.'))

