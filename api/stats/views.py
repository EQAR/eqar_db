import datetime

from django.conf import settings
from django.db.models import Count, Max, Q, F, ExpressionWrapper, DurationField, Avg
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

from rest_framework import generics, status, views, viewsets, permissions, serializers
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from uni_db.filters import FilterBackend

from contacts.models import Contact
from agencies.models import \
    Applications, \
    RegisteredAgency, \
    ApplicationStandard, \
    EsgStandard, \
    ApplicationRole

from stats.helpers import Esg, EsgList
from stats.serializers import ApplicationsListSerializer, ApplicationStandardListSerializer

from rest_framework import pagination

# toolbox

@method_decorator(cache_control(max_age=settings.STATS_CACHE_MAX_AGE), name='dispatch')
class StatsView(views.APIView):
    """
    Generic view for stats

    These attributed should be defined in subclass, or the get_xyz() methods overwritten:

    queryset     - Queryset from which stats are generated
    x_range      - X axis range
    field_labels - dict( [field name]: [column label], ... )

    Optional field:
    x_name       - field that takes X axis value (default: first field name)
    """
    permission_classes = [ ] # default is public

    def _default_get(self, attribute, default=None):
        if hasattr(self, attribute):
            return getattr(self, attribute)
        elif default:
            return default
        else:
            raise NotImplementedError(f'you must either set the {attribute} attribute or implement get_{attribute}()')

    def get_queryset(self):
        return self._default_get('queryset')

    def get_x_range(self):
        return self._default_get('x_range')

    def get_field_labels(self):
        return self._default_get('field_labels')

    def get_renderer_context(self):
        context = super().get_renderer_context()
        labels = self.get_field_labels()
        if isinstance(labels, dict):
            context['labels'] = labels
            context['header'] = tuple(labels)
        elif isinstance(labels, (tuple, list)):
            context['header'] = labels
        else:
            raise TypeError('field_labels must be either dict or tuple')
        return context

    def get_x_name(self):
        if hasattr(self, 'x_name'):
            return self.x_name
        else:
            return list(self.get_field_labels())[0]

    def filter_queryset_by_x(self, x, **kwargs):
        """
        filter the queryset for a given x-axis value
        """
        raise NotImplementedError('function filter_queryset_by_x() must be implemented')

    def stats(self, filtered_qs, x, **kwargs):
        """
        return stats using a filtered queryset - should return a dict
        """
        raise NotImplementedError('function stats() must be implemented')

    def x_to_str(self, x):
        """
        turn X axis value to label - can be overwritten if needed
        """
        return str(x)

    def iterate_over_x(self, **kwargs):
        stats = [ ]
        for x in self.get_x_range():
            this = self.stats(self.filter_queryset_by_x(x, **kwargs), x, **kwargs)
            this[self.get_x_name()] = self.x_to_str(x)
            stats.append(this)
        return stats

    def get_stats(self):
        return self.iterate_over_x()

    def get(self, request, format=None):
        self.request = request
        self.format = format
        return Response(self.get_stats(), status=status.HTTP_200_OK)

class PerYearStatsView(StatsView):
    """
    generic view for by-year stats
    """

    def get_year_start(self):
        return self._default_get('year_start', 2008)

    def get_year_last(self):
        return self._default_get('year_last', datetime.date.today().year)

    def get_x_range(self):
        return range(self.get_year_start(), self.get_year_last() + 1)

# these views are primarily for the EQAR website

class OpenApplications(generics.ListAPIView):
    """
    list current/open applications
    """
    permission_classes = [ permissions.IsAuthenticated ]
    queryset = Applications.objects.exclude(stage__in=['8. Completed', '-- Withdrawn']).order_by('stage', '-submitDate')
    serializer_class = ApplicationsListSerializer
    pagination_class = None
    filter_backends = [FilterBackend, OrderingFilter]
    filterset_fields = [ 'type', 'stage', 'agency', 'secretary' ]

class WithdrawnApplications(generics.ListAPIView):
    """
    list applications that were withdrawn
    """
    permission_classes = [ permissions.IsAuthenticated ]
    queryset = Applications.objects.filter(stage='-- Withdrawn').order_by('-submitDate')
    serializer_class = ApplicationsListSerializer
    pagination_class = None

# precedent list

class ApplicationPrecedentList(generics.ListAPIView):
    """
    list of precedents
    """
    permission_classes = [ permissions.IsAuthenticated ]
    queryset = ApplicationStandard.objects.exclude(keywords__isnull=True, decision__isnull=True)
    serializer_class = ApplicationStandardListSerializer
    filter_backends = [FilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        'application__agency': [ 'exact' ],
        'application__agency__baseCountry': [ 'exact' ],
        'application__type': [ 'exact' ],
        'application__review': [ 'exact' ],
        'application__coordinator': [ 'exact' ],
        'application__decisionDate': [ 'gt', 'lt', 'year' ],
        'standard': [ 'exact' ],
        'rc': [ 'exact' ],
        'panel': [ 'exact' ],
    }
    search_fields = [ 'standard__title', 'application__agency__shortname', 'keywords', 'decision' ]

# following views are primarily for datawrapper.io charts

class ApplicationsTimeline(PerYearStatsView):
    """
    return number of applications and registered agencies by year
    """
    queryset = Applications.objects.all()
    field_labels = {
            'year': 'Year',
            'applications': 'Decisions on applications',
            'agencies': 'Registered agencies',
        }

    def filter_queryset_by_x(self, year, **kwargs):
        return self.queryset.filter(decisionDate__year=year)

    def stats(self, filtered_qs, year, **kwargs):
        first = datetime.date(year, 1, 1)
        last = datetime.date(year, 12, 31)
        return({
            'applications': filtered_qs.count(),
            'agencies': RegisteredAgency.objects.filter(registeredSince__lte=last, validUntil__gte=first).count() if year != self.get_year_last()
                        else RegisteredAgency.objects.filter(registered=True).count(),
        })


class ApplicationsTotals(StatsView):
    """
    return application results by type
    """
    queryset = Applications.objects.filter(Q(stage='-- Withdrawn') | Q(stage='8. Completed'))
    field_labels = {
            'result': 'Result',
            'initial': 'Initial applications',
            'renewal': 'Renewal applications',
        }

    def get_x_range(self):
        return [ i['result'] for i in self.get_queryset().order_by().values('result').distinct() ]

    def filter_queryset_by_x(self, x, **kwargs):
        return self.get_queryset().filter(result=x)

    def stats(self, filtered_qs, x, **kwargs):
        return {
            'initial': filtered_qs.filter(type='Initial').count(),
            'renewal': filtered_qs.filter(type='Renewal').count(),
        }


class ComplianceStats(StatsView):
    """
    show compliance by ESG standard
    """
    queryset = ApplicationStandard.objects.filter(application__stage='8. Completed')
    x_range = EsgStandard.objects.filter(version__active=True)
    field_labels = (
            'standard',
            'Compliance',
            'Partial compliance',
            'Non-compliance',
        )

    def filter_queryset_by_x(self, esg, **kwargs):
        return self.get_queryset().filter(standard=esg, **kwargs)

    def x_to_str(self, esg):
        return esg.short_name

    def stats(self, filtered_qs, esg, *args, **kwargs):
        stats = {}
        for compliance in ('Compliance', 'Partial compliance', 'Non-compliance'):
            stats[compliance] = filtered_qs.filter(rc=compliance).count()
        return stats


class ComplianceExtendedStats(ComplianceStats):
    """
    show compliance by ESG standard, broken down by types, years and agencies
    """
    def __init__(self):
        self.year_range = range(2016, self.get_queryset().aggregate(last=Max('application__decisionDate'))['last'].year + 1)

    def get_stats(self, **kwargs):
        stats = {
            'All': self.iterate_over_x()
        }
        for application_type in ('Initial', 'Renewal'):
            stats[application_type] = self.iterate_over_x(application__type=application_type)
        for result in ('Approved', 'Rejected'):
            stats[result] = self.iterate_over_x(application__result=result)
        for year in self.year_range:
            stats[year] = self.iterate_over_x(application__decisionDate__year=year)
        return stats


class ComplianceChangeMixin:
    """
    common attributes and methods for stats on compliance-level change
    """
    queryset = ApplicationStandard.objects.filter(application__stage='8. Completed', panel__isnull=False, rc__isnull=False)
    field_labels = {
        'total': 'Total per-standard conclusions',
        'downgrade': 'Conclusion downgraded',
        'downgrade_share': 'Conclusion downgraded (percentage)',
        'identical': 'Conclusion identical',
        'identical_share': 'Conclusion identical (percentage)',
        'upgrade': 'Conclusion upgraded',
        'upgrade_share': 'Conclusion upgraded (percentage)',
    }

    Q_identical =   Q(rc=F('panel')) | \
                    Q(panel='Full compliance', rc='Compliance') | \
                    Q(panel='Substantial compliance', rc='Compliance')
    Q_downgrade =   ( ( Q(panel='Compliance') | Q(panel='Full compliance') | Q(panel='Substantial compliance') ) & ~Q(rc='Compliance') ) | \
                    Q(panel='Partial compliance', rc='Non-compliance')
    Q_upgrade =     ( Q(panel='Non-compliance') & ~Q(rc='Non-compliance') ) | \
                    Q(panel='Partial compliance', rc='Compliance')

    def stats(self, filtered_qs, *args, **kwargs):
        this = {
            'total':        filtered_qs.count(),
            'identical':    filtered_qs.filter(self.Q_identical).count(),
            'downgrade':    filtered_qs.filter(self.Q_downgrade).count(),
            'upgrade':      filtered_qs.filter(self.Q_upgrade).count(),
        }
        for i in ('identical','downgrade','upgrade'):
            this[f'{i}_share'] = this[i] / this['total'] if this['total'] else 0
        return this


class ComplianceChangeStats(ComplianceChangeMixin, PerYearStatsView):
    """
    statistics on change to panel's conclusion per standard - by year
    """
    year_start = 2016
    field_labels = { 'year': 'Year', **ComplianceChangeMixin.field_labels }

    def get_year_last(self):
        return self.get_queryset().aggregate(last=Max('application__decisionDate'))['last'].year

    def filter_queryset_by_x(self, year, **kwargs):
        return self.get_queryset().filter(application__decisionDate__year=year)


class ComplianceChangePerStandardStats(ComplianceChangeMixin, StatsView):
    """
    statistics on change to panel's conclusion per standard - by standard
    """
    field_labels = { 'standard': 'Standard', **ComplianceChangeMixin.field_labels }
    x_range = EsgStandard.objects.filter(version__active=True)

    def filter_queryset_by_x(self, esg, **kwargs):
        return self.get_queryset().filter(standard=esg)


class ComplianceChangePerPanelStats(ComplianceChangeMixin, StatsView):
    """
    statistics on change to panel's conclusion - by panel members
    """
    field_labels = { 'person': 'Panel member', **ComplianceChangeMixin.field_labels }
    x_range = Contact.objects.annotate(
                    review_count=Count(
                        'application_role',
                        filter=Q(applicationrole__role__in=[
                            'Panel member',
                            'Panel chair',
                            'Panel secretary',
                        ])
                    )
                ).filter(review_count__gte=4)

    def filter_queryset_by_x(self, contact, **kwargs):
        return self.get_queryset().filter(application__roles=contact)


class ComplianceChangePerRapporteurStats(ComplianceChangeMixin, StatsView):
    """
    statistics on change to panel's conclusion - by RC rapporteurs
    """
    field_labels = { 'person': 'RC rapporteur', **ComplianceChangeMixin.field_labels }
    x_range = Contact.objects.filter(organisation=48, contactorganisation__function__startswith='RC')

    def filter_queryset_by_x(self, contact, **kwargs):
        return self.get_queryset().filter(Q(application__rapporteur1=contact) | Q(application__rapporteur2=contact))


class ApplicationStatsMixin:
    """
    common queryset for most application statistics
    """
    queryset = Applications.objects.filter(stage='8. Completed')

class ApplicationByYearMixin:
    """
    common parameters for rich year-by-year stats on applications
    """
    year_start = 2016

    def get_year_last(self):
        return self.get_queryset().aggregate(last=Max('decisionDate'))['last'].year

    def filter_queryset_by_x(self, year, **kwargs):
        return self.get_queryset().filter(decisionDate__year=year)

class ApplicationDurationMixin:
    """
    calculate times between application, eligibility confirmation, report and decision
    """
    zero_date = 'reportDate'
    include_dates = [
        'submitDate',
        'eligibilityDate',
        'sitevisitDate',
        'reportDate',
        'reportSubmitted',
        'decisionDate',
    ]

    field_labels = {
            'label': 'Application',
            'd_submitDate': 'Application submitted',
            'd_eligibilityDate': 'Eligibility confirmed',
            'd_sitevisitDate': 'Site-visit date',
            'd_reportDate': 'Report date',
            'd_reportSubmitted': 'Report submitted',
            'd_decisionDate': 'RC decision',
        }

    def _timedelta(self, a, b=None):
        if b is None:
            b = self.zero_date
        return ExpressionWrapper(F(a)-F(b), output_field=DurationField())

    def stats(self, filtered_qs, year, **kwargs):
        # generate annotation expressions for timedeltas
        aggregate_kwargs = { }
        for date in self.include_dates:
            if date != self.zero_date:
                aggregate_kwargs[f'd_{date}'] = Avg(self._timedelta(date))
        # run query and transform values to ordinary list
        values = filtered_qs.aggregate(**aggregate_kwargs)
        values[f'd_{self.zero_date}'] = 0
        # convert timedeltas to days
        for date in self.include_dates:
            if isinstance(values[f'd_{date}'], datetime.timedelta):
                values[f'd_{date}'] = values[f'd_{date}'].days
        return values


class ApplicationsDuration(ApplicationDurationMixin, StatsView):
    """
    duration for X latest applications
    """
    queryset = Applications.objects.exclude(Q(stage__lte='2. Waiting report') | Q(stage='-- Withdrawn')).order_by('-reportSubmitted')
    default_limit = 10
    zero_date = 'reportSubmitted'
    field_labels = { 'label': 'Application', **ApplicationDurationMixin.field_labels }

    def get_x_range(self):
        # limit to the X latest cases
        limit = int(self.request.query_params.get('limit', self.default_limit))
        return self.get_queryset()[0:limit]

    def filter_queryset_by_x(self, application, **kwargs):
        return self.get_queryset().filter(pk=application.pk)

    def x_to_str(self, application):
        return(f'{application.reportSubmitted} {application.agency} (A{application.id} {application.type}, {application.review})')


class ApplicationsDurationPerYear(ApplicationDurationMixin, ApplicationStatsMixin, ApplicationByYearMixin, PerYearStatsView):
    """
    return times between application, eligibility confirmation, report and decision
    """
    zero_date = 'reportSubmitted'
    field_labels = { 'year': 'Year', **ApplicationDurationMixin.field_labels }

    def get_year_last(self):
        return self.get_queryset().aggregate(last=Max('reportSubmitted'))['last'].year

    def filter_queryset_by_x(self, year, **kwargs):
        return self.get_queryset().filter(reportSubmitted__year=year)


class ClarificationRequestStatsMixin:
    """
    statistics on number of clarificaiton requests
    """
    field_labels = {
            'total': 'Applications total',
            'request_panel': 'Requests to panel',
            'request_panel_share': 'Requests to panel (percentage)',
            'request_coordinator': 'Requests to coordinator',
            'request_coordinator_share': 'Requests to coordinator (percentage)',
            'request_agency': 'Requests to agency',
            'request_agency_share': 'Requests to agency (percentage)',
            'request_other': 'Requests to others',
            'request_other_share': 'Requests to others (percentage)',
        }

    def stats(self, filtered_qs, x, **kwargs):
        this = {
            'total':                filtered_qs.count(),
            'request_panel':        filtered_qs.filter(applicationclarification__type='Panel', **kwargs).distinct().count(),
            'request_coordinator':  filtered_qs.filter(applicationclarification__type='Coordinator', **kwargs).distinct().count(),
            'request_agency':       filtered_qs.filter(applicationclarification__type='Agency', **kwargs).distinct().count(),
            'request_other':        filtered_qs.filter(applicationclarification__type='Other', **kwargs).distinct().count(),
        }
        for t in ('panel','coordinator','agency','other'):
            this[f'request_{t}_share'] = this[f'request_{t}'] / this['total']
        return this


class ClarificationRequestsByYearStats(ClarificationRequestStatsMixin, ApplicationStatsMixin, ApplicationByYearMixin, PerYearStatsView):
    """
    clarificaiton requests - by year
    """
    field_labels = { 'year': 'Year', **ClarificationRequestStatsMixin.field_labels }


class ClarificationRequestsByStandardStats(ClarificationRequestStatsMixin, ApplicationStatsMixin, StatsView):
    """
    clarificaiton requests - by ESG
    """
    field_labels = { 'standard': 'ESG', **ClarificationRequestStatsMixin.field_labels }

    x_range = EsgStandard.objects.filter(version__active=True)

    def filter_queryset_by_x(self, esg, **kwargs):
        return self.get_queryset()

    def x_to_str(self, esg):
        return esg.short_name

    def stats(self, filtered_qs, esg, **kwargs):
        filter_kwargs = { f'applicationclarification__esg_{esg.attribute_name}': True }
        return super().stats(filtered_qs, esg, **filter_kwargs)


# following views are designed for Infogram/Prezi

class ComplianceTimelineByStandard(ApplicationStatsMixin, ApplicationByYearMixin, PerYearStatsView):
    """
    show compliance by year for each ESG standard
    """
    field_labels = (
            'year',
            'Compliance',
            'Partial compliance',
            'Non-compliance',
        )

    def stats(self, filtered_qs, year, esg, **kwargs):
        this = { }
        for count in filtered_qs.exclude(**{f'{esg.rc}__isnull': True}).values(esg.rc).annotate(n=Count('id')).order_by(esg.rc):
            this[count[esg.rc]] = count['n']
        return this

    def get_stats(self, **kwargs):
        stats = { }
        for esg in EsgList():
            stats[str(esg)] = self.iterate_over_x(esg=esg, **kwargs)
        return stats
