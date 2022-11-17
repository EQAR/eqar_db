from django.db.models import Q

from uni_db.views import ModelViewSet, UniModelViewSet

from agencies.models import *

from contacts.models import Contact, Organisation

class EsgVersionViewSet(UniModelViewSet):
    queryset = EsgVersion.objects.all()
    unidb_options = { 'readonly': True }
    relations_count = (
        'esgstandard_set',
    )

class EsgStandardViewSet(UniModelViewSet):
    queryset = EsgStandard.objects.all()
    list_fields = [ 'version', 'part', 'number', 'title' ]
    filterset_fields = [ 'version', 'part' ]
    unidb_options = { 'readonly': True }
    relations_count = (
        'applicationstandard_set',
    )

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
        'applicationstandard_set',
    )
    limit_choices_to = {
        'rapporteur1':  Q(organisation=48, contactorganisation__function__startswith='RC'),
        'rapporteur2':  Q(organisation=48, contactorganisation__function__startswith='RC'),
        'rapporteur3':  Q(organisation=48, contactorganisation__function__startswith='RC'),
        'secretary':    Q(organisation=48, contactorganisation__function__startswith='SEC'),
        'coordinator':  Q(pk__in=Applications.objects.values('coordinator').distinct()),
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

class ApplicationStandardViewSet(UniModelViewSet):
    queryset = ApplicationStandard.objects.all()
    list_fields = [ 'application', 'standard', 'panel', 'rapporteurs', 'rc', 'keywords' ]
    search_fields = [ 'standard__title', 'application__agency__shortname', 'keywords', 'decision' ]
    filterset_fields = {
        'application': [ 'exact' ],
        'standard': [ 'exact' ],
        'panel': [ 'exact' ],
        'rapporteurs': [ 'exact' ],
        'rc': [ 'exact' ],
        'keywords': [ 'isnull' ],
    }
    unidb_options = { 'delete': False, 'create': False }

class ChangeReportViewSet(UniModelViewSet):
    queryset = ChangeReport.objects.all()
    list_fields = [ 'agency', 'submitDate', 'stage', 'decisionDate', 'result' ]
    filterset_fields = [ 'agency', 'stage', 'secretary', 'result' ]
    search_fields = [ 'agency__shortname', 'agency__organisation__longname' ]
    limit_choices_to = {
        'rapporteur1':  Q(organisation=48, contactorganisation__function__startswith='RC'),
        'rapporteur2':  Q(organisation=48, contactorganisation__function__startswith='RC'),
        'secretary':    Q(organisation=48, contactorganisation__function__startswith='SEC'),
    }

class ComplaintViewSet(UniModelViewSet):
    queryset = Complaint.objects.all()
    list_fields = [ 'agency', 'stage', 'submitDate', 'decisionDate', 'result' ]
    filterset_fields = [ 'agency', 'stage', 'secretary', 'result' ]
    search_fields = [ 'agency__shortname', 'agency__organisation__longname' ]
    limit_choices_to = {
        'rapporteur1':  Q(organisation=48, contactorganisation__function__startswith='RC'),
        'rapporteur2':  Q(organisation=48, contactorganisation__function__startswith='RC'),
        'secretary':    Q(organisation=48, contactorganisation__function__startswith='SEC'),
    }
