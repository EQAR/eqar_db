from agencies.models import RegisteredAgency, \
                            AgencyUpdate, \
                            Applications, ApplicationClarification, ApplicationInterest, ApplicationRole, \
                            ChangeReport, \
                            Complaint

from contacts.models import Contact, Organisation
from contacts.serializers import OrganisationSerializer

from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer

from uni_db.serializers import ListSerializer, DetailSerializer, RelationsCount

class AgencyListSerializer(ListSerializer):
    class Meta:
        model = RegisteredAgency
        fields = [ 'shortname', 'organisation', 'registered', 'registered_since', 'valid_until', 'base_country' ]

class AgencySerializer(WritableNestedModelSerializer):
    _related = RelationsCount('agencyupdate_set', 'applications_set') #, 'changereport_set')
    organisation = OrganisationSerializer()

    class Meta:
        model = RegisteredAgency
        fields = '__all__'

class AgencyUpdateListSerializer(ListSerializer):
    class Meta:
        model = AgencyUpdate
        fields = [ 'agency', 'year', 'type', 'country', 'cross_border', 'amount', 'source' ]

class AgencyUpdateSerializer(DetailSerializer):
    class Meta:
        model = AgencyUpdate
        fields = '__all__'

class ApplicationListSerializer(ListSerializer):
    class Meta:
        model = Applications
        fields = [ 'agency', 'type', 'submit_date', 'stage', 'rapporteur1', 'rapporteur2', 'secretary' ]

class ApplicationSerializer(DetailSerializer):
#_related = RelationsCount('applicationclarification_set', 'applicationinterest_set', 'applicationrole_set')
    rapporteur1 = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.filter(organisation=48))
    rapporteur2 = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.filter(organisation=48))
    rapporteur3 = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.filter(organisation=48))
    secretary = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.filter(organisation=48))
    coordinator = serializers.PrimaryKeyRelatedField(queryset=Organisation.objects.filter(pk__in=Applications.objects.values('coordinator').distinct()))

    def validate(self, data):
        """
        Some sanity checks
        """
        if data['stage'] == '8. Completed' and not data['result']:
            raise serializers.ValidationError("Decisions needs to be specified for completed decisions.")
        return data

    class Meta:
        model = Applications
        fields = '__all__'

