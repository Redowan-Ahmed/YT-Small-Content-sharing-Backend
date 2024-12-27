from rest_framework import viewsets
from channel.documents import ContentDocument
from .serializers import ContentBasicSearchSerializer, ContentmainSearchSerializer
from channel.models import Content
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    DefaultOrderingFilterBackend,
    CompoundSearchFilterBackend,
    OrderingFilterBackend,
    FunctionalSuggesterFilterBackend,
    MultiMatchSearchFilterBackend,
    SearchFilterBackend
)
from django_elasticsearch_dsl_drf.pagination import QueryFriendlyPageNumberPagination

class BasicSearchView(DocumentViewSet):
    document = ContentDocument
    serializer_class = ContentBasicSearchSerializer
    # http_method_names = ['get']
    lookup_field = 'id'
    filter_backends = [
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
        FunctionalSuggesterFilterBackend,
        MultiMatchSearchFilterBackend
    ]
    # functional_suggester_fields = ['title']
    pagination_class = QueryFriendlyPageNumberPagination
    search_fields = {
        'title': {'fuzziness': 'AUTO'},
        'description': {'fuzziness': 'AUTO'},
    }

    ordering_fields = {
        'title': 'title',
        '_score': '_score',
    }

    multi_match_search_fields = (
        'title',
        'description',
    )
    ordering = ('_score')
