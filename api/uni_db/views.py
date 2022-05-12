from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from uni_db.metadata import ExtendedMetadata
from uni_db.mixins import ReadWriteSerializerMixin
from uni_db.filters import FilterBackend
from uni_db.serializers import ListSerializer, DetailSerializer
from uni_db.permissions import IsSuperUser, AllowReadOnly

class ModelViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    """
    adapted ModelViewSet class with some defaults
    """
    metadata_class = ExtendedMetadata
    permission_classes = [permissions.IsAuthenticated & (IsSuperUser | AllowReadOnly) ]
    filter_backends = [FilterBackend, SearchFilter, OrderingFilter]

    def get_field_order(self):
        return [ i.name for i in self.get_queryset().model._meta.fields ]

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = self.get_field_order()
        return context

    def get_lookup_url_kwarg(self):
        return(self.lookup_url_kwarg or self.lookup_field)

    def is_object(self):
        return(self.get_lookup_url_kwarg() in self.kwargs)

    def is_collection(self):
        return(not self.is_object())

    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        queryset = self.filter_queryset(self.get_queryset())

        assert self.is_object(), (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, self.get_lookup_url_kwarg())
        )

        if 'key' in self.request.query_params:
            filter_kwargs = {self.request.query_params['key']: self.kwargs[self.get_lookup_url_kwarg()]}
        else:
            filter_kwargs = {self.lookup_field: self.kwargs[self.get_lookup_url_kwarg()]}

        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class UniModelViewSet(ModelViewSet):
    """
    extended ModelViewSet that generates serializers automatically
    """

    @action(detail=True, methods=['get'])
    def nested(self, request, pk=None):
        obj = self.queryset.get(pk=pk)
        serializer = self.get_nested_serializer_class()
        return Response(serializer(obj).data)

    @action(detail=False, methods=['get'])
    def select(self, request):
        results = self.filter_queryset(self.queryset)
        serializer = self.get_search_serializer_class()
        return Response(serializer(results, many=True).data)

    @action(detail=False, methods=['get'])
    def download(self, request):
        results = self.filter_queryset(self.queryset)
        serializer = self.get_download_serializer_class()
        return Response(serializer(results, many=True).data)

    def _add_limit_choices_to(self, target):
        for field, q in getattr(self, 'limit_choices_to', {}).items():
            if field in target.Meta.extra_kwargs:
                target.Meta.extra_kwargs[field]['limit_choices_to'] = q
            else:
                target.Meta.extra_kwargs[field] = { 'limit_choices_to': q }

    def _make_serializer_class(self, baseclass, ref_name, details):

        class ThisSerializer(baseclass):
            class Meta:
                pass

        ThisSerializer.Meta.model = self.queryset.model
        ThisSerializer.Meta.ref_name = f'{self.queryset.model._meta.model_name}-{ref_name}'
        ThisSerializer.Meta.extra_kwargs = getattr(self, 'extra_kwargs', dict())
        if details:
            ThisSerializer.Meta.fields = '__all__'
        else:
            ThisSerializer.Meta.fields = getattr(self, 'list_fields', '__all__')
        return(ThisSerializer)

    def get_list_serializer_class(self):
        return(self._make_serializer_class(ListSerializer, 'list', False))

    def get_search_serializer_class(self):
        SearchSerializer = self._make_serializer_class(ListSerializer, 'search', False)
        SearchSerializer.Meta.fields = [ '_label' ]
        return(SearchSerializer)

    def get_download_serializer_class(self):
        return(self._make_serializer_class(ListSerializer, 'download', True))

    def get_read_serializer_class(self):
        ReadSerializer = self._make_serializer_class(DetailSerializer, 'detail', True)
        if hasattr(self, 'relations_count'):
            ReadSerializer.Meta.relations_count = self.relations_count
        self._add_limit_choices_to(ReadSerializer)
        return(ReadSerializer)

    def get_nested_serializer_class(self):
        NestedSerializer = self._make_serializer_class(DetailSerializer, 'nested', True)
        NestedSerializer.Meta.depth = 2
        return(NestedSerializer)

    def get_write_serializer_class(self):
        WriteSerializer = self._make_serializer_class(DetailSerializer, 'write', True)
        self._add_limit_choices_to(WriteSerializer)
        return(WriteSerializer)

