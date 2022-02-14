import datetime

from django.db.models import Count, Max
from django.shortcuts import render

from rest_framework import generics, status, views, viewsets, permissions, serializers
from rest_framework.response import Response

from agencies.models import Applications, RegisteredAgency

from stats.helpers import Esg, EsgList
from stats.serializers import ApplicationsListSerializer
from stats.renderers import InfogramJSONRenderer

# these views are primarily for the EQAR website

class OpenApplications(generics.ListAPIView):
    """
    list current/open applications
    """
    permission_classes = [ permissions.IsAuthenticated ]
    queryset = Applications.objects.exclude(stage__in=['8. Completed', '-- Withdrawn']).order_by('stage', '-submitDate')
    serializer_class = ApplicationsListSerializer
    pagination_class = None

class WithdrawnApplications(generics.ListAPIView):
    """
    list applications that were withdrawn
    """
    permission_classes = [ permissions.IsAuthenticated ]
    queryset = Applications.objects.filter(stage='-- Withdrawn').order_by('-submitDate')
    serializer_class = ApplicationsListSerializer
    pagination_class = None

# following views are primarily for datawrapper.io charts

class ApplicationsTimeline(views.APIView):
    """
    return number of applications and registered agencies by year
    """
    permission_classes = [ ]
    START = 2008

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = (
            'year',
            'applications',
            'agencies',
        )
        context['labels'] = {
            'year': 'Year',
            'applications': 'Decisions on applications',
            'agencies': 'Registered agencies',
        }
        return context

    def get(self, request, format=None):
        stats = []
        current_year = datetime.date.today().year
        for year in range(self.START, current_year + 1):
            first = datetime.date(year, 1, 1)
            last = datetime.date(year, 12, 31)
            stats.append({
                'year': year,
                'applications': Applications.objects.filter(decisionDate__year=year).count(),
                'agencies': RegisteredAgency.objects.filter(registeredSince__lte=last, validUntil__gte=first).count() if year != current_year
                        else RegisteredAgency.objects.filter(registered=True).count(),
            })
        return Response(stats, status=status.HTTP_200_OK)

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
    renderer_classes = [ InfogramJSONRenderer ]

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

