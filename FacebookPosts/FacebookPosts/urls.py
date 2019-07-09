from django.contrib import admin
from django.urls import path
from PostData import views
from django.conf.urls import include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('create_post/', views.create_post),
    path('add_comment/', views.add_comment),
    path('add_reply/', views.reply_to_comment),
    path('add_post_reaction/', views.react_to_post),
    path('add_comment_reaction/', views.react_to_comment),
    path('get_posts/', views.get_user_posts),
    path('get_positive_posts/', views.get_posts_with_more_positive_reactions),
    path('get_user_reacted_posts/', views.get_posts_reacted_by_user),
    path('get_reactions_to_post/', views.get_reactions_to_post),
    path('get_reaction_metrics_to_post/', views.get_reaction_metrics),
    path('get_total_reactions/', views.get_total_reaction_count),
    path('get_comment_replies/', views.get_replies_for_comment),
    path('post/<int:post_id>', views.get_post),
    path('users/', views.user_list),
    path('delete_post/', views.delete_post),
    path('api-auth/', include('rest_framework.urls')),
]
