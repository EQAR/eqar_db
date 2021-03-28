from rest_framework.metadata import SimpleMetadata
from rest_framework.serializers import RelatedField, ManyRelatedField

class ForeignKeyChoicesMetadata(SimpleMetadata):

    """
    Metadata class that returns list of possible choices for foreign key fields
    """

    def get_field_info(self, field):
        field_info = super().get_field_info(field)
        if (not field_info.get('read_only') and isinstance(field, (RelatedField, ManyRelatedField)) and hasattr(field, 'choices')):
            field_info['choices'] = [
                {
                    'value': choice_value,
                    'display_name': choice_name
                }
                for choice_value, choice_name in field.choices.items()
            ]
        return(field_info)
