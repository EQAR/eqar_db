from django.shortcuts import render
from django.db.models import Count

from rest_framework import pagination

from uni_db.views import ModelViewSet

from agencies.models import RegisteredAgency, Applications, AgencyUpdate
from agencies.serializers import \
    AgencySerializer, AgencyListSerializer, \
    ApplicationSerializer, ApplicationListSerializer, \
    AgencyUpdateSerializer, AgencyUpdateListSerializer

class AgencyViewSet(ModelViewSet):
    queryset = RegisteredAgency.objects.all()
    list_serializer_class = AgencyListSerializer
    read_serializer_class = AgencySerializer
    write_serializer_class = AgencySerializer

class ApplicationViewSet(ModelViewSet):
    queryset = Applications.objects.all()
    list_serializer_class = ApplicationListSerializer
    read_serializer_class = ApplicationSerializer
    write_serializer_class = ApplicationSerializer
    filterset_fields = [ 'type', 'result', 'stage', 'secretary' ]

class AgencyUpdateViewSet(ModelViewSet):
    queryset = AgencyUpdate.objects.all()
    list_serializer_class = AgencyUpdateListSerializer
    read_serializer_class = AgencyUpdateSerializer
    write_serializer_class = AgencyUpdateSerializer
    filterset_fields = [ 'agency', 'year', 'type', 'country', 'cross_border', 'source' ]
    search_fields = [ 'agency', 'year', 'country__name' ]

