from django.db.models import Count
from django.forms.models import ModelChoiceIteratorValue

from rest_framework import pagination

from django_filters import ChoiceFilter, NumberFilter
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

    def get_filterset(self, request, queryset, view):
        """
        no custom behaviour, but the method saves the generated filterset in the
        current request instance, so it can later on be used for generating facets
        """
        filterset = super().get_filterset(request, queryset, view)
        request.filterset = filterset
        return(filterset)


class SearchFacetPagination(pagination.LimitOffsetPagination):
    """
    custom pagination class that adds options and record counts for searchable fields
    """

    def paginate_queryset(self, queryset, request, view=None):
        """
        no custom behaviour here, but we need QuerySet and View objects later on
        (they're not passed to the function we actually customise)
        """
        self.qs = queryset
        self.view = view
        self.request = request
        return(super().paginate_queryset(queryset, request, view))

    def get_paginated_response(self, data):
        r = super().get_paginated_response(data) # data as original class returns it
        filterset_fields = getattr(self.view, 'filterset_fields', None)
        facets = { }
        for field, filter in self.request.filterset.get_filters().items():
            if isinstance(filter, (ChoiceFilter, NumberFilter)):
                facet = [ ]
                if isinstance(filter, ChoiceFilter):
                    labels = { ( value.value if isinstance(value, ModelChoiceIteratorValue) else value ): label for value, label in filter.field.choices }
                for choice in self.qs.values(field).annotate(_count=Count(field)).order_by(field):
                    if choice['_count'] > 0:
                        if isinstance(filter, ChoiceFilter) and choice[field] in labels:
                            facet.append((choice[field], choice['_count'], labels[choice[field]]))
                        else:
                            facet.append((choice[field], choice['_count']))
                facets[field] = facet
        r.data['facets'] = facets   # augment by search facets
        return(r)

