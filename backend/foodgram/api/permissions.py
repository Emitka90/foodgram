from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from django.http import HttpResponseNotAllowed
from rest_framework.response import Response


class IsOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


class IsAdminOrReadOnly(BasePermission):
    code = 'default_code'

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS or request.user and request.user.is_staff)