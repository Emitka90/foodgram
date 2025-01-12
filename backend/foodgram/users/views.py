from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.permissions import (
    IsAuthenticated,
)

from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Follow
from .serializers import (
    CustomUserSerializer,
    PasswordSerializer,
    AvatarSerializer,
    FollowSerializer
)

User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

        

    def perform_create(self, serializer):
        if "password" in self.request.data:
            password = make_password(self.request.data["password"])
            serializer.save(password=password)
        else:
            serializer.save()

    def perform_update(self, serializer):
        if "password" in self.request.data:
            password = make_password(self.request.data["password"])
            serializer.save(password=password)
        else:
            serializer.save()


    @action(
        methods=["get"], detail=False, permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
    

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        user = self.request.user
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"status": "password set"})
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=["put"], detail=False, permission_classes=[IsAuthenticated], url_path="me/avatar")
    def set_avatar(self, request):
        avatar_data = request.data.get('avatar')
        if not avatar_data:
            return Response({'detail': 'Требуется аватар.'}, status=status.HTTP_400_BAD_REQUEST)
        user = self.request.user
        serializer = AvatarSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'avatar': user.avatar.url}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @set_avatar.mapping.delete
    def del_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Аватар не найден.'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(methods=["post"], detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, id=pk)
        if user == author:
            return Response({
                'errors': 'Вы не можете подписываться на самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, author=author).exists():
            return Response({
                'errors': 'Вы уже подписаны на данного пользователя'
            }, status=status.HTTP_400_BAD_REQUEST)

        follow = Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, id=pk)
        if user == author:
            return Response({
                'errors': 'Вы не можете отписываться от самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({
            'errors': 'Вы уже отписались'
        }, status=status.HTTP_400_BAD_REQUEST)
    



#    @action(detail=False, permission_classes=[IsAuthenticated])
#    def subscriptions(self, request):
#        user = request.user
#        queryset = Follow.objects.filter(user=user)
#        pages = self.paginate_queryset(queryset)
#        serializer = FollowSerializer(
#            pages,
#            many=True,
#            context={'request': request}
#        )
#        return self.get_paginated_response(serializer.data)
