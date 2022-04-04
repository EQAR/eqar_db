from contacts.models import Contact, Organisation, Country
from agencies.models import Applications, RegisteredAgency
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

