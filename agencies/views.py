from uni_db.views import ModelViewSet, UniModelViewSet

from agencies.models import *

from contacts.models import Contact, Organisation

class AgencyViewSet(UniModelViewSet):
    queryset = RegisteredAgency.objects.all()
    list_fields = [ 'shortname', 'organisation', 'registered', 'registered_since', 'valid_until', 'base_country' ]
    filterset_fields = [ 'base_country', 'registered', 'valid_until' ]
    relations_count = ('agencyupdate_set', 'applications_set', 'changereport_set')

class ApplicationViewSet(UniModelViewSet):
    queryset = Applications.objects.all()
    list_fields = [ 'agency', 'type', 'submit_date', 'stage', 'rapporteur1', 'rapporteur2', 'secretary' ]
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
    list_fields = [ 'agency', 'year', 'type', 'country', 'cross_border', 'amount', 'source' ]
    filterset_fields = [ 'agency', 'year', 'type', 'country', 'cross_border', 'source' ]
    search_fields = [ 'agency', 'year', 'country__name' ]

class ApplicationRoleViewSet(UniModelViewSet):
    queryset = ApplicationRole.objects.all()
    list_fields = [ 'application', 'contact', 'notes' ]

class ApplicationClarificationViewSet(UniModelViewSet):
    queryset = ApplicationClarification.objects.all()
    filterset_fields = [ 'application', 'type' ]
    list_fields = [ 'application', 'type', 'sent_on', 'reply_on' ]

class ApplicationInterestViewSet(UniModelViewSet):
    queryset = ApplicationInterest.objects.all()
    list_fields = [ 'application', 'contact' ]

class ChangeReportViewSet(UniModelViewSet):
    queryset = ChangeReport.objects.all()
    list_fields = [ 'agency', 'submit_date', 'stage', 'decision_date', 'result' ]
    relations_querysets = {
        'rapporteur1': Contact.objects.filter(organisation=48),
        'rapporteur2': Contact.objects.filter(organisation=48),
        'secretary':   Contact.objects.filter(organisation=48),
    }

class ComplaintViewSet(UniModelViewSet):
    queryset = Complaint.objects.all()
    list_fields = [ 'agency', 'stage', 'submit_date', 'decision_date', 'result' ]

