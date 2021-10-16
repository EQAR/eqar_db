from rest_framework import viewsets, permissions

from uni_db.views import ModelViewSet, UniModelViewSet

from contacts.models import *

class ContactViewSet(UniModelViewSet):
    queryset = Contact.objects.all()
    list_fields = [ 'lastname', 'firstname', 'email', 'phone', 'mobile' ]
    search_fields = [ 'lastname', 'firstname', 'email', 'phone', 'mobile' ]

class OrganisationViewSet(UniModelViewSet):
    queryset = Organisation.objects.all()
    list_fields = [ 'acronym', 'longname', 'role', 'city', 'country' ]
    search_fields = [ 'acronym', 'longname', 'city', 'country__name', 'postcode' ]
    filterset_fields = [ 'role', 'city', 'country' ]

class ContactOrganisationViewSet(UniModelViewSet):
    queryset = ContactOrganisation.objects.all()
    list_fields = [ 'contact', 'organisation', 'sendofficial', 'senddeqar', 'sendinvoice' ]
    filterset_fields = [ 'contact', 'organisation', 'sendofficial', 'senddeqar' ]

class OctopusAccountViewSet(UniModelViewSet):
    queryset = OctopusAccount.objects.all()
    list_fields = [ 'organisation', 'octopus_id', 'client', 'supplier' ]

class DeqarConnectPartnerViewSet(UniModelViewSet):
    queryset = DeqarConnectPartner.objects.all()
    list_fields = [ 'organisation', 'type', 'pic', 'contact_technical', 'contact_admin' ]
    filterset_fields = [ 'type' ]

class DeqarPartnerViewSet(UniModelViewSet):
    queryset = DeqarPartner.objects.all()
    list_fields = [ 'organisation', 'type', 'pic', 'technician', 'manager' ]
    filterset_fields = [ 'type' ]

class CountryViewSet(UniModelViewSet):
    queryset = Country.objects.all()
    list_fields = [ 'name', 'capital', 'ehea', 'eu', 'iso3', 'iso2' ]
    filterset_fields = [ 'ehea', 'eu', 'eter' ]
    search_fields = [ 'longname', 'longname_local', 'name', 'name_local', 'capital' ]
    unidb_options = { 'delete': False }
    relations_count = ('organisation_set', 'registeredagency_set', 'contact_set', 'agencyupdate_set')

class LanguageViewSet(UniModelViewSet):
    queryset = Language.objects.all()
    unidb_options = { 'delete': False, 'update': False }

class RoleViewSet(UniModelViewSet):
    queryset = Role.objects.all()
    unidb_options = { 'readonly': True }

