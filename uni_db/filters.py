from django.db.models import Count

from rest_framework import pagination

from django_filters import ChoiceFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet

from uni_db.fields import EnumField

class FilterBackend(DjangoFilterBackend):
    """
    default filter backend with support for EnumField added
    """

    def get_filterset_class(self, view, queryset=None):
        filterset_fields = getattr(view, 'filterset_fields', None)

        if filterset_fields and queryset is not None:
            MetaBase = getattr(FilterSet, 'Meta', object)

            class AutoFilterSet(FilterSet):
                class Meta(MetaBase):
                    model = queryset.model
                    fields = filterset_fields
                    filter_overrides = {
                        EnumField: {
                            'filter_class': ChoiceFilter,
                        },
                    }

            return AutoFilterSet

        return None

class SearchFacetPagination(pagination.LimitOffsetPagination):
    """
    custom pagination class that adds options and record counts for searchable fields
    """

    def paginate_queryset(self, queryset, request, view=None):
        """
        no custom behaviour here, but we need QuerySet and View objects later on
        (they're not passed to the function we actually customise)
        """
        if (request.accepted_renderer.media_type in [ 'text/csv' ]):
            # this disables pagination when downloading
            return(None)
        else:
            self.qs = queryset
            self.view = view
            return(super().paginate_queryset(queryset, request, view))

    def get_paginated_response(self, data):
        r = super().get_paginated_response(data) # data as original class returns it
        filterset_fields = getattr(self.view, 'filterset_fields', None)
        if filterset_fields is not None:
            facets = { }
            for field in filterset_fields:
                model_field = self.qs.model._meta.get_field(field)
                facet = [ ]
                for choice in self.qs.values(field).annotate(_count=Count(field)).order_by(field):
                    if model_field.is_relation and choice[field]:
                        facet.append((choice[field], choice['_count'], model_field.related_model.objects.get(pk=choice[field]).__str__()))
                    else:
                        facet.append((choice[field], choice['_count']))
                facets[field] = facet
            r.data['facets'] = facets   # augment by search facets
        return(r)

