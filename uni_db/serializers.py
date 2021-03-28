from rest_framework import serializers

class RelationsCount(serializers.Field):
    """
    field to include numbers of related records in detail serializers
    """

    def __init__(self, *fields, **kwargs):
        self._fields = fields
        return(super().__init__(read_only=True, **kwargs))

    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        reverse = []
        for f in self._fields:
            try:
                revmgr = getattr(value, f)
                reverse.append({
                    "relatedTable": revmgr.model._meta.object_name.lower(),
                    "count": revmgr.count(),
                    "column": revmgr.field.target_field.name,
                    "relatedColumn": revmgr.field.name,
                    "unique": False,
                    "value": getattr(value, revmgr.field.target_field.name)
                })
            except AttributeError:
                raise Exception(f"Unknown field or not a reverse relationship: `{f}` in `{value._meta.object_name}` object")
        return reverse


class ListSerializer(serializers.ModelSerializer):
    """
    default serializer for list view

    relational fields as strings, and __str__ added to field list as label
    """
    _label = serializers.CharField(source='__str__', read_only=True)

    def __init__(self, *args, **kwargs):
        if hasattr(self.Meta, 'fields') and type(self.Meta.fields) == list:
            if '_label' not in self.Meta.fields:
                self.Meta.fields.append('_label')
            if self.Meta.model._meta.pk.name not in self.Meta.fields:
                self.Meta.fields.insert(0, self.Meta.model._meta.pk.name)
        super().__init__(*args, **kwargs)

    def build_relational_field(self, field_name, relation_info):
        return( (serializers.StringRelatedField, { 'read_only': True }) )

class DetailSerializer(serializers.ModelSerializer):
    """
    default serializer for detail view

    __str__ is added to field list as label
    """
    _label = serializers.CharField(source='__str__', read_only=True)

