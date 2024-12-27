from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Content, Category, Channel, Tag


@registry.register_document
class ContentDocument(Document):
    category = fields.ObjectField(properties={
        'category_name': fields.TextField(),
    })
    channel = fields.ObjectField(properties={
        'channel_name': fields.KeywordField(),
    })
    tags = fields.ObjectField(properties={
        'name': fields.KeywordField(),
    })

    class Index:
        name = 'contents'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Content
        fields = ['title', 'description', 'thumbnail', 'views_count', 'duration', 'id', 'created_at', 'updated_at']
        related_models = [Category, Channel, Tag]

    def get_queryset(self):
        return super(ContentDocument, self).get_queryset().select_related(
            'category', 'channel'
        )