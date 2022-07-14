from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer

import phonenumbers

from lxml import etree

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
        'member',
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

class XMLRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """
    media_type = "application/xml"
    format = "xml"
    charset = "utf-8"
    item_tag_name = "list-item"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ""
        return etree.tostring(data, pretty_print=True)

class GxpAddressBook(APIView):
    permission_classes = []
    renderer_classes = (XMLRenderer,)

    group_id = "2"
    group_name = "EQAR DB"

    def get(self, request, *args, **kwargs):
        def TextElement(tag, text):
            e = etree.Element(tag)
            e.text = text
            return e

        def format_phone_number(raw_number):
            try:
                parsed = phonenumbers.parse(raw_number)
                return phonenumbers.format_out_of_country_calling_number(parsed, 'BE')
            except:
                return raw_number

        abook = etree.Element("AddressBook")
        group = etree.Element("pbgroup")
        group.append(TextElement("id", self.group_id))
        group.append(TextElement("name", self.group_name))
        abook.append(group)
        for item in ContactOrganisation.objects.all():
            contact = etree.Element("Contact")
            contact.append(TextElement("FirstName", item.contact.firstName))
            contact.append(TextElement("LastName", item.contact.lastName))
            contact.append(TextElement("Department", item.organisation.name))
            contact.append(TextElement("Group", self.group_id))
            if item.contact.phone:
                phone = etree.Element("Phone", type="Work")
                phone.append(TextElement("phonenumber", format_phone_number(item.contact.phone)))
                phone.append(TextElement("accountindex", "1"))
                contact.append(phone)
            if item.contact.mobile:
                phone = etree.Element("Phone", type="Cell")
                phone.append(TextElement("phonenumber", format_phone_number(item.contact.mobile)))
                phone.append(TextElement("accountindex", "1"))
                contact.append(phone)
            abook.append(contact)

        return Response(abook, content_type='application/xml')

