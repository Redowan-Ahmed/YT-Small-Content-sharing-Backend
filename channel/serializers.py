from rest_framework import serializers
from .models import Channel, Like, Dislike, Comment, Category, Content, VideoFile
from account.serializers import UserMeSerializer

class UserChannelSerializer(serializers.ModelSerializer):
    admin = UserMeSerializer()
    associated_user = UserMeSerializer(many = True)
    class Meta:
        model = Channel
        fields = '__all__'


class ChannelSerializer(serializers.ModelSerializer):
    subscribers = serializers.SerializerMethodField()
    class Meta:
        model = Channel
        fields = ['channel_name', 'channel_slug', 'channel_picture', 'channel_banner', 'about', 'subscribers', 'total_views']

    def get_subscribers(self, obj):
        return obj.subscriber.count()


class BasicChannelSerializer(serializers.ModelSerializer):
    subscribers = serializers.SerializerMethodField()
    class Meta:
        model = Channel
        fields = ['channel_name', 'channel_slug', 'channel_picture', 'subscribers']

    def get_subscribers(self, obj):
        return obj.subscriber.count()

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'


class DislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dislike
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class VideoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = ['file', 'user', 'channel', 'content']



class BasicContentSerializer(serializers.ModelSerializer):
    videos = serializers.SerializerMethodField()
    channel = BasicChannelSerializer()

    class Meta:
        model = Content
        fields = ['id', 'created_at', 'title', 'thumbnail', 'views_count', 'status', 'category', 'channel', 'tags', 'videos', 'duration']

    def get_videos(self, obj):
        return obj.videos.all().values_list('hsl_file', flat=True)

class ContentSerializer(serializers.ModelSerializer):
    videos = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    channel = BasicChannelSerializer()

    class Meta:
        model = Content
        fields = ['id', 'created_at', 'updated_at', 'title', 'description', 'thumbnail', 'views_count', 'status', 'category', 'channel', 'tags', 'videos', 'likes', 'dislikes', 'duration']

    def get_dislikes(self, obj):
        return obj.dislikes.count()

    def get_likes(self, obj):
        return obj.likes.count()

    def get_videos(self, obj):
        return obj.videos.all().values_list('hsl_file', flat=True)

