from django.shortcuts import get_object_or_404
from rest_framework import viewsets, views
from .models import Channel, Category, Comment, Like, Dislike, Content, VideoFile
from .serializers import CategorySerializer, UserChannelSerializer, ChannelSerializer, ContentSerializer, BasicContentSerializer, VideoFileSerializer, LikeSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework_extensions.mixins import NestedViewSetMixin
from django.contrib.auth import get_user_model
from django.db.models import Case, When, BooleanField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.response import Response
from .tasks import add
import random

class UserChannelView(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Channel.objects
    serializer_class = UserChannelSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'channel_slug'

    def get_queryset(self):
        return self.queryset.filter(Q(admin=self.request.user) | Q(associated_user__id__exact=self.request.user.id))


class ChannelView(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    lookup_field = 'channel_slug'
    http_method_names = ['get']


class ContentView(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Content.objects
    serializer_class = BasicContentSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'category__category_slug',
                        'tags', 'created_at', 'views_count']
    search_fields = ['title']

    def get_queryset(self):
        data = self.queryset.filter(channel__channel_slug__exact=self.kwargs.get(
            'parent_lookup_channel_slug')).prefetch_related('videos')
        return data


class HomeContentView(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Content.objects.select_related('author', 'category', 'channel')
    serializer_class = BasicContentSerializer
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {'category': ['exact'], 'category__category_slug': ['exact'], 'tags': [
        'exact'], 'created_at': ['exact'], 'views_count': ['gte', 'lte', 'range']}  # ADvance Query
    search_fields = ['title']
    ordering_fields = ['created_at', 'views_count']

    def get_queryset(self):
        singleContent = self.kwargs.get(self.lookup_field)
        if self.request.user.is_authenticated:
            try:
                if self.action == 'retrieve':
                    obj = self.queryset.filter(pk=singleContent)
                    if obj:
                        try:
                            upOb = obj.first()
                            upOb.viewers.add(self.request.user)
                        except Exception as e:
                            print(e)
                    return obj

                user = get_object_or_404(get_user_model().objects.prefetch_related(
                    'viewed'), pk=self.request.user.pk)

                viewed_categories = user.viewed.values_list(
                    'category__id', flat=True).distinct()[:20]
                viewed_ids = user.viewed.values_list('id', flat=True)

                # related_content = self.queryset.filter(
                #     Q(category__id__in=viewed_categories)
                # ).annotate(
                #     is_viewed=Case(
                #         When(id__in=viewed_ids, then=True),
                #         default=False,
                #         output_field=BooleanField()
                #     )
                # ).order_by('is_viewed', '?').distinct()

                related_content = self.queryset.all().annotate(
                    is_viewed=Case(
                        When(id__in=viewed_ids, then=True),
                        default=False,
                        output_field=BooleanField()
                    ),
                    ViewedCat=Case(
                        When(category__id__in=viewed_categories, then=True),
                        default=False,
                        output_field=BooleanField()
                    )
                ).order_by('-ViewedCat', 'is_viewed').distinct()

                return related_content
            except Exception as e:
                raise e

        return self.queryset.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ContentSerializer
        return BasicContentSerializer


class RelatedContentsView(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Content.objects
    serializer_class = BasicContentSerializer
    http_method_names = ['get']
    def get_queryset(self):
        try:
            content = get_object_or_404(
                Content, pk=self.kwargs.get('parent_lookup_pk'))
            rTags = content.tags.all().values_list('id', flat=True)
            uniqueContent = self.queryset.filter(Q(category=content.category), Q(tags__id__in=rTags)).exclude(pk=content.pk).distinct('pk')
            uniqueContent = list(uniqueContent)
            random.shuffle(uniqueContent)
            return uniqueContent
        except Exception as e:
            return Response({'error': e})


class CategoriesView(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Category.objects
    serializer_class = CategorySerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = get_object_or_404(get_user_model().objects.prefetch_related(
                'viewed'), pk=self.request.user.pk)
            viewed_categories = user.viewed.values_list(
                'category__id', flat=True).distinct()[:20]
            return self.queryset.all().annotate(
                viwedCat=Case(
                    When(id__in=viewed_categories, then=True),
                    default=False,
                    output_field=BooleanField()
                )
            ).order_by('-viwedCat', '?')
        return self.queryset.all()


class VideoUploadView(viewsets.ModelViewSet):
    queryset = VideoFile.objects.all()
    serializer_class = VideoFileSerializer
    parser_classes = [FileUploadParser]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'delete']

    def create(self, request, *args, **kwargs):
        try:
            channelObj = Channel.objects.get(channel_slug=self.kwargs.get('parent_lookup_channel_slug'))
            if channelObj.admin == self.request.user or self.request.user in channelObj.associated_user.all():
                try:
                    content = Content.objects.get(id=self.kwargs.get('parent_lookup_id'))
                    if content:
                        if content.channel.id == channelObj.id:
                            if not content.videos.all():
                                file = request.data['file']
                                if not file:
                                    return Response({
                                        'status': status.HTTP_400_BAD_REQUEST,
                                        'message': 'No file provided'
                                    })
                                data = {
                                    'file': file,
                                    'user': self.request.user.id,
                                    'channel': channelObj.id,
                                    'content': content.id,
                                }
                                serializer = self.get_serializer(data = data)
                                serializer.is_valid(raise_exception= True)
                                self.perform_create(serializer)
                                return Response({
                                    'status': status.HTTP_201_CREATED,
                                    'message': 'Video uploaded successfully',
                                })
                            else:
                                return Response({
                                    'status': status.HTTP_200_OK,
                                    'message': 'This content already have a video',
                                })
                    else:
                        return Response({
                            'status': status.HTTP_406_NOT_ACCEPTABLE,
                            'message': 'You are not authorized or able to upload video for this content'
                        })
                except Exception as e:
                    return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Content ID is invalid', 'error': e})
            else:
                return Response({
                    'status': status.HTTP_401_UNAUTHORIZED,
                    'message': 'You are not authorized or team member to upload video to this channel',
                })
        except Exception as e:
            return Response({
                'status': status.HTTP_404_NOT_FOUND,
                'message': f'Something Went Wrong',
                'error': e
            })


class LikesView(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes =[IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def create(self, request, *args, **kwargs):
        try:
            contentId = request.data.get('content')
            userId = request.user.id
            data = {
                'content': contentId,
                'user': userId,
            }
            serializer = self.serializer_class(data = data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': status.HTTP_201_CREATED, 'message': 'Like added successfully'})
            else:
                return Response({'status': status.HTTP_406_NOT_ACCEPTABLE, 'message': 'Invalid data received'})
        except Exception as e:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'message': 'Content ID is not found', 'error': e})

    def get_queryset(self):
        likes = self.queryset.filter(user = self.request.user).order_by('-created_at')
        return likes


# class FileUploadView(views.APIView):
#     parser_classes = [FileUploadParser]

#     def post(self, request, format=None):
#         try:
#             channel_slug = request.query_params.get('channel_slug')
#             content_id = request.query_params.get('content_id')

#             # Ensure channel_slug and content_id are provided
#             if not channel_slug or not content_id:
#                 return Response(
#                     {"message": "channel_slug and content_id are required parameters"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             channelObj = get_object_or_404(Channel, channel_slug=channel_slug)
#             content = get_object_or_404(Content, id=content_id)
#             data = {
#                 'file': request.data['file'],
#                 'user': self.request.user.id,
#                 'channel': channelObj.id,
#                 'content': content.id
#             }
#             # Attempt to get the file from request data
#             try:
#                 file = request.data['file']
#             except Exception as e:
#                 return Response(
#                     {"message": "File parsing error: ensure the request is multipart and contains a file.", "error": str(
#                         e)},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             print(self.request.user.id, channelObj.id, content.id)
#             print(file)
#             serializer = VideoFileSerializer(data=data)
#             print(serializer)
#             print(serializer.is_valid())
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({'status': status.HTTP_201_CREATED, 'message': 'Video uploaded successfully'})

#             # Add additional processing here

#             return Response({"message": "File received successfully"}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"message": "Something went wrong", "error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )