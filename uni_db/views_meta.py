from django.urls import path, include

from rest_framework import status, generics, views, viewsets, permissions, routers
from rest_framework.response import Response

from members.views import MemberViewSet, InvoiceViewSet
from contacts.views import RoleViewSet, OrganisationViewSet, CountryViewSet, ContactViewSet, LanguageViewSet
from agencies.views import AgencyViewSet, ApplicationViewSet, AgencyUpdateViewSet

class UniDB:

    Tables = [
        OrganisationViewSet,
        AgencyViewSet,
        AgencyUpdateViewSet,
        ApplicationViewSet,
        MemberViewSet,
        InvoiceViewSet,
        ContactViewSet,
        CountryViewSet,
        RoleViewSet,
        LanguageViewSet,
    ]

    @classmethod
    def table_path(cls):
        tables = routers.DefaultRouter()
        for viewset in cls.Tables:
            tables.register(tables.get_default_basename(viewset), viewset)

        return(path('table/', include(tables.urls)))

    class TableList(views.APIView):
        """
        List tables available for viewing/editing
        """
        permission_classes = [permissions.IsAuthenticated]

        def get(self, request, format=None):
            tables = dict()
            for viewset in UniDB.Tables:
                slug = routers.DefaultRouter.get_default_basename(None, viewset)
                if hasattr(viewset, 'list_serializer_class'):
                    if viewset.list_serializer_class is not None:
                        list_serializer_class = viewset.list_serializer_class
                    else:
                        list_serializer_class = viewset.read_serializer_class
                else:
                    list_serializer_class = viewset.serializer_class
                list_serializer = list_serializer_class()
                tables[slug] = dict(    name=slug,
                                        description=list_serializer_class.Meta.model._meta.verbose_name_plural,
                                        section='table',
                                        hidden=False,
                                        priKey=list_serializer_class.Meta.model._meta.pk.name,
                                        searchable=True,
                                        includeGlobalSearch=False,
                                        underlyingTable=None,
                                        allowNew=True,
                                        allowEdit=True,
                                        allowDelete=True,
                                        columns={ i: list_serializer.fields[i].label for i in list_serializer.fields },
                                )

            return Response(dict(
                UniDB_motd='Connected: TEST TEST',
                uiconfig=dict(pagetitle='EQAR DB TEST', cuttext=60),
                tables=tables
            ), status=status.HTTP_200_OK)

    class QueryList(views.APIView):
        """
        List queries
        """

        def get(self, request, format=None):
            return Response(dict(
                mtime=None,
                queries=dict()
            ), status=status.HTTP_200_OK)

