from rest_framework import permissions


class IsReviewOwner(permissions.BasePermission):
    """check if request user is owner reviews"""
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
