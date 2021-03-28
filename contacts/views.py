from rest_framework import viewsets, permissions

from uni_db.views import ModelViewSet

from contacts.models import Organisation, Role, Country, Contact, Language
from contacts.serializers import \
    OrganisationSerializer, OrganisationListSerializer, \
    CountrySerializer, CountryListSerializer, \
    ContactSerializer, ContactListSerializer, \
    RoleSerializer, \
    LanguageSerializer

class ContactViewSet(ModelViewSet):
    queryset = Contact.objects.all()
    list_serializer_class = ContactListSerializer
    read_serializer_class = ContactSerializer
    write_serializer_class = ContactSerializer

class OrganisationViewSet(ModelViewSet):
    queryset = Organisation.objects.all()
    list_serializer_class = OrganisationListSerializer
    read_serializer_class = OrganisationSerializer
    write_serializer_class = OrganisationSerializer

class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    #list_serializer_class = RoleListSerializer
    read_serializer_class = RoleSerializer
    write_serializer_class = RoleSerializer

class CountryViewSet(ModelViewSet):
    queryset = Country.objects.all()
    list_serializer_class = CountryListSerializer
    read_serializer_class = CountrySerializer
    write_serializer_class = CountrySerializer

class LanguageViewSet(ModelViewSet):
    queryset = Language.objects.all()
    #list_serializer_class = LanguageListSerializer
    read_serializer_class = LanguageSerializer
    write_serializer_class = LanguageSerializer

