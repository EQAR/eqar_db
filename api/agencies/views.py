from uni_db.views import ModelViewSet, UniModelViewSet

from agencies.models import *

from contacts.models import Contact, Organisation

class AgencyViewSet(UniModelViewSet):
    queryset = RegisteredAgency.objects.all()
    list_fields = [ 'shortname', 'organisation', 'registered', 'registeredSince', 'validUntil', 'baseCountry' ]
    search_fields = [ 'shortname', 'organisation__longname', 'baseCountry__name', 'baseCountry__name_local' ]
    filterset_fields = [ 'baseCountry', 'registered', 'validUntil' ]
    relations_count = (
        'applications_set',
        'changereport_set',
        'agencyupdate_set',
        'complaint_set',
    )

class ApplicationViewSet(UniModelViewSet):
    queryset = Applications.objects.all()
    list_fields = [ 'agency', 'type', 'submitDate', 'stage', 'rapporteur1', 'rapporteur2', 'secretary' ]
    search_fields = [ 'agency__shortname', 'agency__organisation__longname' ]
    filterset_fields = [ 'type', 'result', 'stage', 'agency', 'secretary' ]
    relations_count = (
        'applicationclarification_set',
        'applicationinterest_set',
        'applicationrole_set',
    )
    relations_querysets = {
        'rapporteur1': Contact.objects.filter(organisation=48, contactorganisation__function__startswith='RC'),
        'rapporteur2': Contact.objects.filter(organisation=48, contactorganisation__function__startswith='RC'),
        'rapporteur3': Contact.objects.filter(organisation=48, contactorganisation__function__startswith='RC'),
        'secretary':   Contact.objects.filter(organisation=48, contactorganisation__function__startswith='SEC'),
        'coordinator': Organisation.objects.filter(pk__in=Applications.objects.values('coordinator').distinct())
    }

class AgencyUpdateViewSet(UniModelViewSet):
    queryset = AgencyUpdate.objects.all()
    list_fields = [ 'agency', 'year', 'type', 'country', 'crossBorder', 'amount', 'source' ]
    filterset_fields = [ 'agency', 'year', 'type', 'country', 'crossBorder', 'source' ]

class ApplicationRoleViewSet(UniModelViewSet):
    queryset = ApplicationRole.objects.all()
    list_fields = [ 'application', 'contact', 'role', 'notes' ]
    filterset_fields = [ 'application', 'contact', 'role' ]
    search_fields = [ 'application__agency__shortname', 'application__agency__organisation__longname', 'contact__firstName', 'contact__lastName' ]

class ApplicationClarificationViewSet(UniModelViewSet):
    queryset = ApplicationClarification.objects.all()
    list_fields = [ 'application', 'type', 'recipientOrg', 'recipientContact', 'sentOn', 'replyOn' ]
    filterset_fields = [ 'application', 'type', 'recipientOrg', 'recipientContact' ]

class ApplicationInterestViewSet(UniModelViewSet):
    queryset = ApplicationInterest.objects.all()
    list_fields = [ 'application', 'contact' ]
    filterset_fields = [ 'application', 'contact' ]

class ChangeReportViewSet(UniModelViewSet):
    queryset = ChangeReport.objects.all()
    list_fields = [ 'agency', 'submitDate', 'stage', 'decisionDate', 'result' ]
    filterset_fields = [ 'agency', 'stage', 'secretary', 'result' ]
    search_fields = [ 'agency__shortname', 'agency__organisation__longname' ]
    relations_querysets = {
        'rapporteur1': Contact.objects.filter(organisation=48, contactorganisation__function__startswith='RC'),
        'rapporteur2': Contact.objects.filter(organisation=48, contactorganisation__function__startswith='RC'),
        'secretary':   Contact.objects.filter(organisation=48, contactorganisation__function__startswith='SEC'),
    }

class ComplaintViewSet(UniModelViewSet):
    queryset = Complaint.objects.all()
    list_fields = [ 'agency', 'stage', 'submitDate', 'decisionDate', 'result' ]
    filterset_fields = [ 'agency', 'stage', 'secretary', 'result' ]
    search_fields = [ 'agency__shortname', 'agency__organisation__longname' ]
    relations_querysets = {
        'rapporteur1': Contact.objects.filter(organisation=48, contactorganisation__function__startswith='RC'),
        'rapporteur2': Contact.objects.filter(organisation=48, contactorganisation__function__startswith='RC'),
        'secretary':   Contact.objects.filter(organisation=48, contactorganisation__function__startswith='SEC'),
    }

