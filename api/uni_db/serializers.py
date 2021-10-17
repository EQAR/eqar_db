from rest_framework import serializers
from uni_db.fields import EnumField

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

    - __str__ is added to field list as label
    - related record counts for reverse relationships
    """
    _label = serializers.CharField(source='__str__', read_only=True)
    _related = serializers.SerializerMethodField()

    def get__related(self, obj):
        if hasattr(self.Meta, 'relations_count'):
            reverse = []
            for f in self.Meta.relations_count:
                try:
                    revmgr = getattr(obj, f)
                    reverse.append({
                        "relatedTable": revmgr.model._meta.object_name.lower(),
                        "count": revmgr.count(),
                        "column": revmgr.field.target_field.name,
                        "relatedColumn": revmgr.field.name,
                        "unique": False,
                        "value": getattr(obj, revmgr.field.target_field.name)
                    })
                except AttributeError:
                    raise Exception(f"Unknown field or not a reverse relationship: `{f}` in `{value._meta.object_name}` object")
            return reverse
        else:
            return None

