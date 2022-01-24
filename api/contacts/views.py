from rest_framework import viewsets, permissions

from uni_db.views import ModelViewSet, UniModelViewSet

from contacts.models import *

class ContactViewSet(UniModelViewSet):
    queryset = Contact.objects.all()
    list_fields = [ 'lastName', 'firstName', 'email', 'phone', 'mobile' ]
    search_fields = [ 'lastName', 'firstName', 'email', 'phone', 'mobile' ]
    relations_count = (
        'contactorganisation_set',
        'application_secretary',
        'applicationclarification_set',
        'applicationinterest_set',
        'applicationrole_set',
        'change_report_secretary',
        'complaint_secretary',
    )

class OrganisationViewSet(UniModelViewSet):
    queryset = Organisation.objects.all()
    list_fields = [ 'acronym', 'longname', 'role', 'city', 'country' ]
    search_fields = [ 'acronym', 'longname', 'city', 'country__name', 'postcode' ]
    filterset_fields = [ 'role', 'city', 'country' ]
    relations_count = (
        'contactorganisation_set',
        'octopusaccount',
        'registeredagency',
        'deqarpartner',
        'deqarconnectpartner',
    )

class ContactOrganisationViewSet(UniModelViewSet):
    queryset = ContactOrganisation.objects.all()
    list_fields = [ 'contact', 'organisation', 'sendOfficial', 'sendDeqar', 'sendInvoice' ]
    filterset_fields = [ 'contact', 'organisation', 'sendOfficial', 'sendDeqar' ]

class OctopusAccountViewSet(UniModelViewSet):
    queryset = OctopusAccount.objects.all()
    list_fields = [ 'organisation', 'octopusId', 'client', 'supplier' ]

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

class RoleViewSet(UniModelViewSet):
    queryset = Role.objects.all()
    unidb_options = { 'readonly': True }
    relations_count = (
        'organisation_set',
    )

