from rest_framework import serializers
from channel.models import Content

class ContentBasicSearchSerializer(serializers.ModelSerializer):
    thumbnail = serializers.URLField()
    class Meta:
        model = Content
        fields = ('id', 'title', 'thumbnail', 'views_count')

class ContentmainSearchSerializer(serializers.ModelSerializer):
    thumbnail = serializers.URLField()

    class Meta:
        model = Content
        fields = ('id', 'title', 'thumbnail', 'views_count', 'description', 'duration', 'channel' )