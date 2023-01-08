import datetime

from django.conf import settings
from django.db.models import Count, Max, Q
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

from rest_framework import generics, status, views, viewsets, permissions, serializers
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from uni_db.filters import FilterBackend

from agencies.models import Applications, RegisteredAgency, ApplicationStandard

from stats.helpers import Esg, EsgList
from stats.serializers import ApplicationsListSerializer, ApplicationStandardListSerializer

from rest_framework import pagination

# toolbox

class PerYearStatsView(views.APIView):
    """
    generic view for by-year stats
    """

    queryset = None # overwrite in subclass

    def __init__(self):
        if not hasattr(self, 'queryset'):
            self.queryset = self.get_queryset()
        if not hasattr(self, 'year_start'):
            self.year_start = self.get_year_start()
        if not hasattr(self, 'year_last'):
            self.year_last = self.get_year_last()
        self.year_range = range(self.year_start, self.year_last + 1)

    def get_queryset(self):
        raise NotImplementedError('you must either set the queryset attribute or implement get_queryset()')

    def get_year_start(self):
        return 2008

    def get_year_last(self):
        return datetime.date.today().year

    def filter_queryset_by_year(self, year, **kwargs):
        """
        filter the queryset for a given year
        """
        raise NotImplementedError('function filter_queryset_by_year() must be implemented')

    def stats(self, filtered_qs, year, **kwargs):
        """
        return stats using a filtered queryset - should return a dict
        """
        raise NotImplementedError('function stats() must be implemented')

    def iterate_over_years(self, **kwargs):
        stats = [ ]
        for year in self.year_range:
            this = self.stats(self.filter_queryset_by_year(year, **kwargs), year, **kwargs)
            this['year'] = year
            stats.append(this)
        return stats

    def get_stats(self, **kwargs):
        return self.iterate_over_years(**kwargs)

    def get(self, request, format=None):
        return Response(self.get_stats(request=request, format=format), status=status.HTTP_200_OK)

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

@method_decorator(cache_control(max_age=settings.STATS_CACHE_MAX_AGE), name='dispatch')
class ApplicationsTimeline(PerYearStatsView):
    """
    return number of applications and registered agencies by year
    """
    permission_classes = [ ]
    queryset = Applications.objects.all()
    year_start = 2008

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['labels'] = {
            'year': 'Year',
            'applications': 'Decisions on applications',
            'agencies': 'Registered agencies',
        }
        context['header'] = tuple(context['labels'].keys())
        return context

    def filter_queryset_by_year(self, year, **kwargs):
        return self.queryset.filter(decisionDate__year=year)

    def stats(self, filtered_qs, year, **kwargs):
        first = datetime.date(year, 1, 1)
        last = datetime.date(year, 12, 31)
        return({
            'applications': filtered_qs.count(),
            'agencies': RegisteredAgency.objects.filter(registeredSince__lte=last, validUntil__gte=first).count() if year != self.year_last
                        else RegisteredAgency.objects.filter(registered=True).count(),
        })


@method_decorator(cache_control(max_age=settings.STATS_CACHE_MAX_AGE), name='dispatch')
class ApplicationsTotals(views.APIView):
    """
    return application results by type
    """
    permission_classes = [ ]

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['labels'] = {
            'result': 'Result',
            'initial': 'Initial applications',
            'renewal': 'Renewal applications',
        }
        context['header'] = tuple(context['labels'].keys())
        return context

    def get(self, request, format=None):
        stats = {}
        for i in Applications.objects.filter(Q(stage='-- Withdrawn') | Q(stage='8. Completed')).values('result','type').annotate(n=Count('id')).order_by('result', 'type'):
            if i['result'] in stats:
                stats[i['result']][i['type']] = i['n']
            else:
                stats[i['result']] = { i['type']: i['n'] }
        table = []
        for i in stats:
            if i:
                table.append({
                    'result': i,
                    'initial': stats[i].get('Initial', 0),
                    'renewal': stats[i].get('Renewal', 0),
                })
        return Response(table, status=status.HTTP_200_OK)

@method_decorator(cache_control(max_age=settings.STATS_CACHE_MAX_AGE), name='dispatch')
class ComplianceStats(views.APIView):
    """
    show compliance by ESG standard
    """
    permission_classes = [ ]

    queryset = Applications.objects.filter(stage='8. Completed')

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = (
            'standard',
            'Compliance',
            'Partial compliance',
            'Non-compliance',
        )
        return context

    def filtered_stats(self, **kwargs):
        stats = []
        for esg in EsgList():
            this = { 'standard': str(esg) }
            for count in self.queryset.exclude(**{f'{esg.rc}__isnull': True}).filter(**kwargs).values(esg.rc).annotate(n=Count('id')).order_by(esg.rc):
                this[count[esg.rc]] = count['n']
            stats.append(this)
        return stats

    def get(self, request, format=None):
        return Response(self.filtered_stats(), status=status.HTTP_200_OK)

# following views are designed for Infogram/Prezi

class ComplianceExtendedStats(ComplianceStats):
    """
    show compliance by ESG standard, broken down by types, years and agencies
    """
    permission_classes = [ ]

    year_start = 2016

    def __init__(self):
        self.year_last = self.queryset.aggregate(last=Max('decisionDate'))['last'].year

    def get(self, request, format=None):
        stats = {
            'All': self.filtered_stats()
        }
        for application_type in ('Initial', 'Renewal'):
            stats[application_type] = self.filtered_stats(type=application_type)
        for result in ('Approved', 'Rejected'):
            stats[result] = self.filtered_stats(result=result)
        for year in range(self.year_start, self.year_last + 1):
            stats[year] = self.filtered_stats(decisionDate__year=year)

        return Response(stats, status=status.HTTP_200_OK)

