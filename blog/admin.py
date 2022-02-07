from django.contrib import admin
from .models import Category, Post, Content, Text, Image, Video, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class ContentInline(admin.StackedInline):
    model = Content
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ContentInline]


admin.site.register(Content)


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ['id', 'text']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'image']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'url']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'created', 'active']
