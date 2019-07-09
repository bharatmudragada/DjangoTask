from rest_framework import permissions
from .models import Post
from django.core.exceptions import ObjectDoesNotExist


class IsOwner(permissions.BasePermission):

    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if 'id' in request.data:
                try:
                    post = Post.objects.get(pk=request.data['id'])
                    return post.user == request.user
                except ObjectDoesNotExist:
                    return False
        return True
