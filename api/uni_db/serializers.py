from django.db.models import Manager
from rest_framework import serializers
from uni_db.fields import EnumField

class StringRelatedField(serializers.StringRelatedField):
    def __init__(self, *args, **kwargs):
        kwargs.pop('limit_choices_to', None)
        super().__init__(*args, **kwargs)

class PrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, *args, **kwargs):
        self.limit_choices_to = kwargs.pop('limit_choices_to', None)
        super().__init__(*args, **kwargs)

class ListSerializer(serializers.ModelSerializer):
    """
    default serializer for list view

    relational fields as strings, and __str__ added to field list as label
    """
    _label = serializers.CharField(source='__str__', read_only=True)

    serializer_related_field = StringRelatedField

    def __init__(self, *args, **kwargs):
        if hasattr(self.Meta, 'fields') and type(self.Meta.fields) == list:
            if '_label' not in self.Meta.fields:
                self.Meta.fields.append('_label')
            if self.Meta.model._meta.pk.name not in self.Meta.fields:
                self.Meta.fields.insert(0, self.Meta.model._meta.pk.name)
        super().__init__(*args, **kwargs)

    def build_relational_field(self, field_name, relation_info):
        return( (StringRelatedField, { 'read_only': True }) )

class DetailSerializer(serializers.ModelSerializer):
    """
    default serializer for detail view

    - __str__ is added to field list as label
    - related record counts for reverse relationships
    """
    _label = serializers.CharField(source='__str__', read_only=True)
    _related = serializers.SerializerMethodField()

    serializer_related_field = PrimaryKeyRelatedField

    def get__related(self, obj):
        if hasattr(self.Meta, 'relations_count'):
            reverse = []
            for f in self.Meta.relations_count:
                try:
                    relation_model = getattr(obj._meta.model, f)
                except AttributeError:
                    raise Exception(f"Unknown field in relations_count: `{f}` in `{obj._meta.object_name}` object")
                else:
                    try:
                        relation = getattr(obj, f)
                    except relation_model.RelatedObjectDoesNotExist:
                        reverse.append({
                            "relatedTable": relation_model.related.related_model._meta.object_name.lower(),
                            "count": 0,
                            "column": relation_model.related.field.target_field.name,
                            "relatedColumn": relation_model.related.field.name,
                            "unique": True,
                            "value": getattr(obj, relation_model.related.field.target_field.name)
                        })
                    else:
                        if isinstance(relation, Manager):
                            reverse.append({
                                "relatedTable": relation.model._meta.object_name.lower(),
                                "count": relation.count(),
                                "column": relation.field.target_field.name,
                                "relatedColumn": relation.field.name,
                                "unique": False,
                                "value": getattr(obj, relation.field.target_field.name)
                            })
                        else:
                            reverse.append({
                                "relatedTable": relation._meta.object_name.lower(),
                                "count": 1,
                                "column": relation_model.related.field.target_field.name,
                                "relatedColumn": relation_model.related.field.name,
                                "unique": True,
                                "value": getattr(obj, relation_model.related.field.target_field.name)
                            })
            return reverse
        else:
            return None

