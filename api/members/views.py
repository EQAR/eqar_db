from rest_framework import viewsets, permissions
from rest_framework.response import Response

from uni_db.views import ModelViewSet, UniModelViewSet

from members.models import Member, Invoice

class MemberViewSet(UniModelViewSet):
    queryset = Member.objects.all()
    list_fields = [ 'id', 'cat', 'name', 'organisation', 'votes' ]
    filterset_fields = [ 'cat', 'votes', 'name', 'organisation' ]
    search_fields = [ 'name', 'signatory', 'function', 'organisation__longname', 'organisation__acronym' ]
    relations_count = (
        'invoice_set',
    )

class InvoiceViewSet(UniModelViewSet):
    queryset = Invoice.objects.all()
    list_fields = [ 'id', 'member', 'account', 'fee']
    filterset_fields = [ 'fee', 'member' ]
    search_fields = [ 'member__name' ]

