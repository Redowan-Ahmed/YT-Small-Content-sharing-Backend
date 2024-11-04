from django.contrib import admin
from .models import Channel, Like, Dislike, Comment, Category, Content, VideoFile, Tag

admin.site.register(Channel)
admin.site.register(Like)
admin.site.register(Dislike)
admin.site.register(Content)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(VideoFile)
admin.site.register(Tag)