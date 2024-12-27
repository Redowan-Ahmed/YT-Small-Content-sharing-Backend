from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from base.models import BaseModel
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
import os
from django.core.exceptions import PermissionDenied, ValidationError
from .tasks import optimize_video
import shutil
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def channel_picture_upload_path(instance, filename):
    return f'channel_picture/{instance.pk}/{filename}'


def channel_banner_upload_path(instance, filename):
    return f'channel_banner/{instance.pk}/{filename}'


def video_upload_path(instance, filename):
    return f'videos/{instance.channel.pk}/{instance.pk}/{filename}'


class Channel(BaseModel):
    channel_name = models.CharField(max_length=255, unique=True, db_index=True)
    admin = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='channel', on_delete=models.CASCADE)
    associated_user = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='channel_associated', blank=True)
    channel_picture = models.ImageField(
        upload_to=channel_picture_upload_path, blank=True)
    channel_banner = models.ImageField(
        upload_to=channel_banner_upload_path, blank=True)
    about = models.TextField(max_length=3000, blank=True)
    website_url = models.URLField(max_length=200, blank=True)
    total_views = models.IntegerField(default=0, blank=True)
    channel_slug = models.SlugField(max_length=500, blank=True)
    subscriber = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='subscribed')

    def __str__(self):
        return self.channel_name

    def save(self,  *args, **kwargs):
        if not self.channel_slug:
            slug = slugify(self.channel_name)
            slug_obj = Channel.objects.filter(channel_slug__contains=slug)
            if slug_obj.exists():
                self.channel_slug = slugify(
                    f'{self.channel_name}-{slug_obj.count() + 1}')
            else:
                self.channel_slug = slug
            print(self.channel_slug)
        super(Channel, self).save(*args, **kwargs)


class Category(BaseModel):
    category_name = models.CharField(
        max_length=255, unique=True, db_index=True)
    category_slug = models.SlugField(max_length=500, blank=True)

    def __str__(self):
        return self.category_name

    def save(self,  *args, **kwargs):
        if not self.category_slug:
            slug = slugify(self.category_name)
            slug_obj = Category.objects.filter(category_slug__contains=slug)
            if slug_obj.exists():
                self.category_slug = slugify(
                    f'{self.category_name}-{slug_obj.count() + 1}')
            else:
                self.category_slug = slug
            print(self.category_slug)
        super(Category, self).save(*args, **kwargs)


class Like(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.ForeignKey(
        'Content', on_delete=models.CASCADE, related_name='likes')

    def __str__(self) -> str:
        return f'{self.user.id} {self.content.title}'

    class Meta:
        unique_together = ('user', 'content')


class Dislike(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.ForeignKey(
        'Content', on_delete=models.CASCADE, related_name='dislikes')

    def __str__(self) -> str:
        return f'{self.user.id} {self.content.title}'

    class Meta:
        unique_together = ('user', 'content')


class Comment(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.ForeignKey(
        'Content', on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(max_length=500, blank=False)
    replied = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='reply', blank=True)

    def __str__(self) -> str:
        return f'{self.user.id} {self.content.title}'


class Tag(BaseModel):
    name = models.CharField(max_length=255, unique=True, db_index=True)

    def __str__(self) -> str:
        return f'{self.name}'


class Content(BaseModel):
    status_choices = (
        ('Draft', 'Draft'),
        ('Published', 'Published'),
        ('Archived', 'Archived'),
        ('Processing', 'Processing'),
        ('Process Completed', 'Process Completed'),
        ('Hide', 'Hide'),
    )
    title = models.CharField(max_length=400, db_index=True)
    description = models.TextField(max_length=3000)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='contents', blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='videos')
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name='contents')
    thumbnail = models.ImageField(upload_to=video_upload_path, max_length=2000)
    viewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='viewed', blank=True)
    views_count = models.IntegerField(blank=True, default=0)
    status = models.CharField(
        max_length=100, db_index=True, default='Draft', choices=status_choices)
    duration = models.CharField(max_length=200, default=0, blank=True)

    def __str__(self) -> str:
        return f'{self.channel.channel_name} - {self.title}'

    def save(self, *args, **kwargs):
        chanel = Channel.objects.get(pk=self.channel.pk)
        print(chanel.associated_user.all())
        if self.author.pk == self.channel.admin.pk or chanel.associated_user.filter(pk=self.author.pk):
            super(Content, self).save(*args, **kwargs)
        else:
            raise ValidationError("You don't have any permission to do it")


class VideoFile(BaseModel):
    file = models.FileField(upload_to=video_upload_path, validators=[
                            FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])], max_length=4000)
    hsl_file = models.FileField(upload_to=video_upload_path, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_videos')
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name='videos')
    content = models.ForeignKey(
        Content, on_delete=models.CASCADE, related_name='videos')

    def __str__(self) -> str:
        return self.channel.channel_name

    def save(self, *args, **kwargs):
        chanel = Channel.objects.get(pk=self.channel.pk)
        print(chanel.associated_user)
        if self.user.pk == self.channel.admin.pk or chanel.associated_user.filter(pk=self.user.pk):
            super(VideoFile, self).save(*args, **kwargs)
        else:
            raise ValidationError("You don't have any permission to do it")




@receiver(post_delete, sender=VideoFile)
def delete_video_file(sender, instance, **kwargs):
    try:
        os.remove(os.path.join(str(settings.MEDIA_ROOT), str(instance.file)))
        dir_path = f'videos/{instance.channel.pk}/{instance.pk}'
        shutil.rmtree(dir_path, ignore_errors=True)
    except Exception as e:
        print('Error deleting the files')


@receiver(post_delete, sender=Content)
def delete_content_associated_instance(sender, instance, **kwargs):
    videoObj = VideoFile.objects.get(pk=instance.video.pk)
    videoObj.delete()
    try:
        os.remove(os.path.join(str(settings.MEDIA_ROOT), str(instance.thumbnail)))
    except Exception as e:
        print('Error deleting the file')
    try:
        os.rmdir(os.path.join(str(settings.MEDIA_ROOT), f'videos/{instance.channel.pk}/{instance.pk}'))
    except Exception as e:
        print('Error deleting the directory')


@receiver(post_save, sender=VideoFile)
def optimizeVideo(sender, instance, created, **kwargs):
    if created:
        optimize_video.delay(str(instance.file), instance.channel.pk, instance.pk)


@receiver(post_save, sender=Like)
def realtimeLikes(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        contentLikes = Content.objects.prefetch_related('likes').get(pk = instance.content.pk).likes.all().count()
        async_to_sync(channel_layer.group_send)(f"like_count_{instance.content.id}", {"type": "like.count", "likes": contentLikes, 'sent_from': f'{instance}_server_like_count'})