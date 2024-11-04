from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import routers
from channel.views import UserChannelView, ChannelView, ContentView, HomeContentView, RelatedContentsView, CategoriesView, VideoUploadView
from rest_framework_extensions.routers import ExtendedDefaultRouter

router = ExtendedDefaultRouter()

router.register('user-channels', UserChannelView, 'user-based-channels').register('contents', ContentView, basename='user-contents', parents_query_lookups=['channel_slug']).register('videoFileUpload', VideoUploadView, basename = 'file-upload', parents_query_lookups=['channel_slug','id'])
router.register('channels', ChannelView, basename='channels').register('contents', ContentView, basename='channel-contents', parents_query_lookups=['channel_slug'])
router.register('contents', HomeContentView, basename = 'home-content').register('related_contents', RelatedContentsView, basename='related-contents', parents_query_lookups=['pk'])
router.register('categories', CategoriesView, basename = 'categories')

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('', include((router.urls, 'api-version-1'))),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('uploadfile/', FileUploadView.as_view()),

    re_path(r'^authentication/', include('djoser.urls')),
    re_path(r'^authentication/', include('djoser.urls.jwt')),
]
