from rest_framework import viewsets, permissions
from rest_framework.response import Response

from uni_db.views import ModelViewSet

from members.models import Member, Invoice
from members.serializers import MemberListSerializer, MemberSerializer, InvoiceListSerializer, InvoiceSerializer


class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    list_serializer_class = MemberListSerializer
    read_serializer_class = MemberSerializer
    write_serializer_class = MemberSerializer
    filterset_fields = [ 'cat', 'votes', 'name', 'organisation' ]
    search_fields = [ 'name', 'signatory', 'function', 'organisation__longname', 'organisation__acronym' ]

class InvoiceViewSet(ModelViewSet):
    queryset = Invoice.objects.all()
    list_serializer_class = InvoiceListSerializer
    read_serializer_class = InvoiceSerializer
    write_serializer_class = InvoiceSerializer
    filterset_fields = [ 'fee', 'member__name' ]
    search_fields = [ 'member__name' ]

