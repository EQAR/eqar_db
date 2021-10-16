import re

from django.urls import path, include
from django.contrib import auth
from django.db import connection
from django.conf import settings

from rest_framework import status, generics, views, viewsets, permissions, routers, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from members.views import *
from contacts.views import *
from agencies.views import *

from uni_db.filters import SearchFacetPagination
from uni_db.mixins import ReadWriteSerializerMixin
from uni_db.models import RawQuery

class UniDB:

    Tables = [
        ContactViewSet,
        OrganisationViewSet,
        ContactOrganisationViewSet,
        OctopusAccountViewSet,
        DeqarConnectPartnerViewSet,
        DeqarPartnerViewSet,
        AgencyViewSet,
        ApplicationViewSet,
        ApplicationRoleViewSet,
        ApplicationInterestViewSet,
        ApplicationClarificationViewSet,
        ChangeReportViewSet,
        ComplaintViewSet,
        AgencyUpdateViewSet,
        MemberViewSet,
        InvoiceViewSet,
        CountryViewSet,
        RoleViewSet,
        LanguageViewSet,
    ]

    @classmethod
    def table_path(cls):
        tables = routers.DefaultRouter()
        for viewset in cls.Tables:
            tables.register(tables.get_default_basename(viewset), viewset)

        return([
            path('table/', include(tables.urls))
        ])

    @classmethod
    def system_path(cls):

        class QuerySerializer(serializers.ModelSerializer):
            owner = serializers.PrimaryKeyRelatedField(
                queryset=auth.models.User.objects.all(),
                default=serializers.CurrentUserDefault()
            )

            class Meta:
                model = RawQuery
                fields = '__all__'

        class QueryViewset(ReadWriteSerializerMixin, viewsets.ModelViewSet):
            """
            List and edit queries
            """
            queryset = RawQuery.objects.all()
            pagination_class = None
            read_serializer_class = QuerySerializer
            write_serializer_class = QuerySerializer
            permission_classes = [permissions.IsAuthenticated]

            def retrieve(self, request, pk=None):
                query = RawQuery.objects.get(pk=pk)
                if not re.match(r'^\s*SELECT', query.sql, re.IGNORECASE):
                    raise PermissionDenied(detail='Raw queries must start with SELECT')

                sql = query.sql
                ordering = request.query_params.get('ordering')
                if ordering:
                    sql = re.sub(r'\s+ORDER\s+BY\s+.*$', '', sql, re.IGNORECASE | re.DOTALL)    # remove ORDER BY if exist
                    sql += " ORDER BY `" + ( ordering[1:] + "` DESC" if ordering[0] == '-' else ordering + "`") # add new ORDER BY clause
                limit = int(request.query_params.get('limit', SearchFacetPagination.default_limit))
                offset = int(request.query_params.get('offset', 0))
                sql += f" LIMIT {limit} OFFSET {offset}"
                with connection.cursor() as cursor:
                    count = cursor.execute(query.sql)
                    cursor.execute(sql)
                    columns = [ col[0] for col in cursor.description ]
                    results = [ dict(zip(columns,row)) for row in cursor.fetchall() ]

                return Response(dict(
                    count=count,
                    columns={ c: c for c in columns },
                    results=results
                ), status=status.HTTP_200_OK)


        queries = routers.DefaultRouter()
        queries.register('query', QueryViewset)
        return([
            path('system/tables/', cls.table_list().as_view()),
            path('', include(queries.urls))
        ])

    @classmethod
    def table_list(cls):

        class TableList(views.APIView):
            """
            List tables available for viewing/editing
            """
            permission_classes = [permissions.IsAuthenticated]

            def get(self, request, format=None):
                tables = dict()
                for viewset in cls.Tables:
                    slug = routers.DefaultRouter.get_default_basename(None, viewset)
                    if hasattr(viewset, 'get_list_serializer_class'):
                        list_serializer_class = viewset().get_list_serializer_class()
                    elif hasattr(viewset, 'get_read_serializer_class'):
                        list_serializer_class = viewset().get_read_serializer_class()
                    else:
                        list_serializer_class = viewset().get_serializer_class()
                    list_serializer = list_serializer_class()
                    def capitalize_first(text):
                        return(text[0].upper() + text[1:])
                    tables[slug] = dict(
                        name=slug,
                        description=capitalize_first(viewset().get_queryset().model._meta.verbose_name_plural),
                        section='table',
                        priKey=viewset().get_queryset().model._meta.pk.name,
                        searchable=hasattr(viewset, 'search_fields'),
                        underlyingTable=None,
                        columns={ i: list_serializer.fields[i].label for i in list_serializer.fields },
                    )
                    options = getattr(viewset, 'unidb_options', {})
                    tables[slug]['hidden'] = options.get('hidden', False)
                    tables[slug]['includeGlobalSearch'] = options.get('includeGlobalSearch', True)
                    if options.get('readonly', False):
                        tables[slug]['allowNew'] = False
                        tables[slug]['allowEdit'] = False
                        tables[slug]['allowDelete'] = False
                    else:
                        tables[slug]['allowNew'] = options.get('create', True)
                        tables[slug]['allowEdit'] = options.get('update', True)
                        tables[slug]['allowDelete'] = options.get('delete', True)

                return Response(dict(
                    UniDB_motd=f'Connected: {settings.UNI_DB_TITLE}',
                    uiconfig=dict(pagetitle=settings.UNI_DB_TITLE, cuttext=60, pagesize=SearchFacetPagination.default_limit),
                    tables=tables
                ), status=status.HTTP_200_OK)

        return(TableList)

