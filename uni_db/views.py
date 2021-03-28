from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

from uni_db.metadata import ForeignKeyChoicesMetadata
from uni_db.mixins import ReadWriteSerializerMixin
from uni_db.filters import FilterBackend

class ModelViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    """
    adapted ModelViewSet class with some defaults
    """

    metadata_class = ForeignKeyChoicesMetadata
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [FilterBackend, SearchFilter, OrderingFilter]

