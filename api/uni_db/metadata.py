from collections import OrderedDict
from rest_framework.metadata import SimpleMetadata
from rest_framework import serializers
from django.db import models

class ExtendedMetadata(SimpleMetadata):

    """
    Metadata class that returns additional information:

    - list of possible choices for foreign key fields
    - field order
    - decimal number length
    - distinguish between CharField and TextField
    """

    def determine_metadata(self, request, view):
        self.request = request
        self.view = view
        if view.is_object():
            self.instance = view.get_object()
        else:
            self.instance = None
        metadata = super().determine_metadata(request, view)
        metadata['field_order'] = view.get_field_order()
        return(metadata)

    def get_field_info(self, field):
        field_info = super().get_field_info(field)
        model_field = getattr(getattr(field.parent.Meta.model, field.source, None), 'field', None)
        if isinstance(field, (serializers.RelatedField, serializers.ManyRelatedField)):
            field_info['foreign_table'] = model_field.related_model._meta.object_name.lower()
            field_info['foreign_key'] = model_field.target_field.name
            if not field_info.get('read_only'):
                choices = OrderedDict()
                if self.instance:
                    foreign_instance = getattr(self.instance, field.field_name)
                    if foreign_instance:
                        choices[getattr(foreign_instance, field_info['foreign_key'])] = str(foreign_instance)
                if getattr(field, 'limit_choices_to', None):
                    queryset = field.queryset.filter(field.limit_choices_to)
                else:
                    queryset = field.queryset.all()
                for choice in queryset.iterator():
                    choices[getattr(choice, field_info['foreign_key'])] = str(choice)
                field_info['choices'] = [
                    {
                        'value': choice_value,
                        'display_name': choice_name
                    }
                    for choice_value, choice_name in choices.items()
                ]
        if isinstance(field, serializers.DecimalField) and model_field:
            field_info['max_digits'] = model_field.max_digits
            field_info['decimal_places'] = model_field.decimal_places
        if isinstance(field, serializers.CharField) and isinstance(model_field, models.TextField):
            field_info['type'] = 'text'
        return(field_info)
