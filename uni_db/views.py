from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response

from uni_db.metadata import ExtendedMetadata
from uni_db.mixins import ReadWriteSerializerMixin
from uni_db.filters import FilterBackend
from uni_db.serializers import ListSerializer, DetailSerializer

class ModelViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    """
    adapted ModelViewSet class with some defaults
    """

    metadata_class = ExtendedMetadata
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [FilterBackend, SearchFilter, OrderingFilter]

    def get_field_order(self):
        return [ i.name for i in self.get_queryset().model._meta.fields ]

    def get_renderer_context(self):
        context = super().get_renderer_context()
        context['header'] = self.get_field_order()
        return context


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

    def _make_serializer_class(self, baseclass, ref_name, details):

        class _ThisSerializer(baseclass):
            class Meta:
                pass

        _ThisSerializer.Meta.model = self.queryset.model
        _ThisSerializer.Meta.ref_name = f'{self.queryset.model._meta.model_name}-{ref_name}'
        _ThisSerializer.Meta.extra_kwargs = getattr(self, 'extra_kwargs', dict())
        if details:
            _ThisSerializer.Meta.fields = '__all__'
        else:
            _ThisSerializer.Meta.fields = getattr(self, 'list_fields', '__all__')
        return(_ThisSerializer)

    def _add_queryset_kwargs(self, target):
        if hasattr(self, 'relations_querysets'):
            for field, qs in self.relations_querysets.items():
                if field in target.Meta.extra_kwargs:
                    target.Meta.extra_kwargs[field]['queryset'] = qs
                else:
                    target.Meta.extra_kwargs[field] = dict(queryset=qs)

    def get_list_serializer_class(self):
        return(self._make_serializer_class(ListSerializer, 'list', False))

    def get_search_serializer_class(self):
        _SearchSerializer = self._make_serializer_class(ListSerializer, 'search', False)
        _SearchSerializer.Meta.fields = [ '_label' ]
        return(_SearchSerializer)

    def get_download_serializer_class(self):
        return(self._make_serializer_class(ListSerializer, 'download', True))

    def get_read_serializer_class(self):
        _ReadSerializer = self._make_serializer_class(DetailSerializer, 'detail', True)
        if hasattr(self, 'relations_count'):
            _ReadSerializer.Meta.relations_count = self.relations_count
        self._add_queryset_kwargs(_ReadSerializer)
        return(_ReadSerializer)

    def get_nested_serializer_class(self):
        _NestedSerializer = self._make_serializer_class(DetailSerializer, 'nested', True)
        _NestedSerializer.Meta.depth = 2
        return(_NestedSerializer)

    def get_write_serializer_class(self):
        _WriteSerializer = self._make_serializer_class(DetailSerializer, 'write', True)
        self._add_queryset_kwargs(_WriteSerializer)
        return(_WriteSerializer)

