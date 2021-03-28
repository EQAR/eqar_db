from members.models import Member, Invoice
from rest_framework import serializers
from contacts.models import Organisation
from contacts.serializers import OrganisationSerializer

from uni_db.serializers import ListSerializer, DetailSerializer

class MemberListSerializer(ListSerializer):
    class Meta:
        model = Member
        fields = [ 'id', 'cat', 'name', 'organisation', 'votes' ]

class MemberSerializer(DetailSerializer):
    class Meta:
        model = Member
        fields = '__all__'

class InvoiceListSerializer(ListSerializer):
    class Meta:
        model = Invoice
        fields = [ 'id', 'member', 'fee']

class InvoiceSerializer(DetailSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

