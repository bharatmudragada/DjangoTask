from django.contrib import admin

# Register your models here.
from .models import User, Post, PostLikes, Comment, CommentLikes


class PostLikesInline(admin.StackedInline):
    model = PostLikes
    extra = 3


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 3


class CommentLikesInline(admin.StackedInline):
    model = CommentLikes
    extra = 3


class PostAdmin(admin.ModelAdmin):
    inlines = [PostLikesInline, CommentInline]


class CommentAdmin(admin.ModelAdmin):
    inlines = [CommentLikesInline]


admin.site.register(User)

admin.site.register(Post, PostAdmin)

admin.site.register(Comment, CommentAdmin)

admin.site.register(PostLikes)

admin.site.register(CommentLikes)