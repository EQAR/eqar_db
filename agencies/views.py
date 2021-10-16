from uni_db.views import ModelViewSet, UniModelViewSet

from agencies.models import *

from contacts.models import Contact, Organisation

class AgencyViewSet(UniModelViewSet):
    queryset = RegisteredAgency.objects.all()
    list_fields = [ 'shortname', 'organisation', 'registered', 'registeredSince', 'validUntil', 'baseCountry' ]
    search_fields = [ 'shortname', 'organisation__longname', 'baseCountry__name', 'baseCountry__name_local' ]
    filterset_fields = [ 'baseCountry', 'registered', 'validUntil' ]
    relations_count = ('agencyupdate_set', 'applications_set', 'changereport_set')

class ApplicationViewSet(UniModelViewSet):
    queryset = Applications.objects.all()
    list_fields = [ 'agency', 'type', 'submitDate', 'stage', 'rapporteur1', 'rapporteur2', 'secretary' ]
    search_fields = [ 'agency__shortname', 'agency__organisation__longname' ]
    filterset_fields = [ 'type', 'result', 'stage', 'agency', 'secretary' ]
    relations_count = ('applicationclarification_set', 'applicationinterest_set', 'applicationrole_set')
    relations_querysets = {
        'rapporteur1': Contact.objects.filter(organisation=48),
        'rapporteur2': Contact.objects.filter(organisation=48),
        'rapporteur3': Contact.objects.filter(organisation=48),
        'secretary':   Contact.objects.filter(organisation=48),
        'coordinator': Organisation.objects.filter(pk__in=Applications.objects.values('coordinator').distinct())
    }

class AgencyUpdateViewSet(UniModelViewSet):
    queryset = AgencyUpdate.objects.all()
    list_fields = [ 'agency', 'year', 'type', 'country', 'crossBorder', 'amount', 'source' ]
    filterset_fields = [ 'agency', 'year', 'type', 'country', 'crossBorder', 'source' ]

class ApplicationRoleViewSet(UniModelViewSet):
    queryset = ApplicationRole.objects.all()
    list_fields = [ 'application', 'contact', 'notes' ]
    search_fields = [ 'application__agency__shortname', 'application__agency__organisation__longname', 'contact__firstname', 'contact__lastname' ]

class ApplicationClarificationViewSet(UniModelViewSet):
    queryset = ApplicationClarification.objects.all()
    filterset_fields = [ 'application', 'type' ]
    list_fields = [ 'application', 'type', 'sentOn', 'replyOn' ]

class ApplicationInterestViewSet(UniModelViewSet):
    queryset = ApplicationInterest.objects.all()
    list_fields = [ 'application', 'contact' ]

class ChangeReportViewSet(UniModelViewSet):
    queryset = ChangeReport.objects.all()
    list_fields = [ 'agency', 'submitDate', 'stage', 'decisionDate', 'result' ]
    search_fields = [ 'agency__shortname', 'agency__organisation__longname' ]
    relations_querysets = {
        'rapporteur1': Contact.objects.filter(organisation=48),
        'rapporteur2': Contact.objects.filter(organisation=48),
        'secretary':   Contact.objects.filter(organisation=48),
    }

class ComplaintViewSet(UniModelViewSet):
    queryset = Complaint.objects.all()
    list_fields = [ 'agency', 'stage', 'submitDate', 'decisionDate', 'result' ]
    search_fields = [ 'agency__shortname', 'agency__organisation__longname' ]

