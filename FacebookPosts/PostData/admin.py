from django.contrib import admin

# Register your models here.
from .models import User, Post, PostReactions, Comment, CommentReactions


class PostReactionsInline(admin.StackedInline):
    model = PostReactions
    extra = 3


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 3


class CommentReactionsInline(admin.StackedInline):
    model = CommentReactions
    extra = 3


class PostAdmin(admin.ModelAdmin):
    inlines = [PostReactionsInline, CommentInline]


class CommentAdmin(admin.ModelAdmin):
    inlines = [CommentReactionsInline]


admin.site.register(User)

admin.site.register(Post, PostAdmin)

admin.site.register(Comment, CommentAdmin)

admin.site.register(PostReactions)

admin.site.register(CommentReactions)