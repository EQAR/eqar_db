from contacts.models import Organisation, Country, Role, Contact, Language
from rest_framework import serializers

from uni_db.serializers import ListSerializer, DetailSerializer, RelationsCount

class ContactListSerializer(ListSerializer):
    class Meta:
        model = Contact
        fields = [ 'firstname', 'lastname', 'email', 'phone', 'mobile' ]

class ContactSerializer(DetailSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class OrganisationListSerializer(ListSerializer):
    class Meta:
        model = Organisation
        fields = [ 'acronym', 'longname', 'city', 'country' ]

class OrganisationSerializer(DetailSerializer):
    class Meta:
        model = Organisation
        fields = '__all__'

class CountryListSerializer(ListSerializer):
    class Meta:
        model = Country
        fields = [ 'name', 'capital', 'ehea', 'eu', 'iso3', 'iso2' ]

class CountrySerializer(DetailSerializer):
    _related = RelationsCount('organisation_set', 'registeredagency_set', 'contact_set', 'agencyupdate_set')
    class Meta:
        model = Country
        fields = '__all__'

#class RoleListSerializer(ListSerializer):
#    class Meta:
#        model = Role
#        fields = '__all__'

class RoleSerializer(DetailSerializer):
    class Meta:
        model = Role
        fields = '__all__'

#class LanguageListSerializer(ListSerializer):
#    class Meta:
#        model = Language
#        fields = '__all__'

class LanguageSerializer(DetailSerializer):
    class Meta:
        model = Language
        fields = '__all__'

