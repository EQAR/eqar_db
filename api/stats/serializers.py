from rest_framework import serializers

from contacts.models import Contact, Organisation, Country
from agencies.models import Applications, RegisteredAgency, ApplicationStandard, ApplicationClarification
from uni_db.serializers import ListSerializer

class _OrganisationSerializer(ListSerializer):

    class Meta:
        model = Organisation
        fields = [ "id", "longname", "acronym" ]


class _CountrySerializer(ListSerializer):
    class Meta:
        model = Country
        fields = [ "iso3", "iso2", "name", "ehea", "eu", "eter" ]


class _ContactSerializer(ListSerializer):

    class Meta:
        model = Contact
        fields = [ "id", "firstName", "lastName", "person" ]


class _AgencySerializer(ListSerializer):
    organisation = _OrganisationSerializer()
    baseCountry = _CountrySerializer()

    class Meta:
        model = RegisteredAgency
        fields = [ "id", "organisation", "shortname", "registered", "deqarId", "baseCountry" ]


class ApplicationsListSerializer(ListSerializer):
    agency = _AgencySerializer()
    coordinator = _OrganisationSerializer()
    secretary = _ContactSerializer()

    class Meta:
        model = Applications
        fields = [
            "id",
            "_label",
            "agency",
            "submitDate",
            "type",
            "review",
            "stage",
            "coordinator",
            "secretary",
            "eligibilityDate",
            "reportExpected",
            "reportDate",
            "reportSubmitted",
            "result",
            "decisionDate",
            "mtime",
        ]

class _ApplicationsSerializer(ListSerializer):
    agency = _AgencySerializer()
    coordinator = _OrganisationSerializer()

    class Meta:
        model = Applications
        fields = [
            "id",
            "_label",
            "agency",
            "submitDate",
            "type",
            "review",
            "coordinator",
            "reportDate",
            "result",
            "decisionDate",
            "mtime",
        ]

class _ApplicationClarificationSerializer(ListSerializer):
    class Meta:
        model = ApplicationClarification
        fields = [ "id", "type", "sentOn", "replyOn" ]

class ApplicationStandardListSerializer(ListSerializer):
    application = _ApplicationsSerializer()
    clarification = serializers.SerializerMethodField()

    def get_clarification(self, obj):
        kwargs = { 'application': obj.application }
        kwargs[f'esg_{obj.standard.attribute_name}'] = True
        return _ApplicationClarificationSerializer(ApplicationClarification.objects.filter(**kwargs), many=True).data

    class Meta:
        model = ApplicationStandard
        fields = [
            "id",
            "application",
            "standard",
            "clarification",
            "panel",
            "rc",
            "keywords",
            "decision",
            "mtime"
        ]

