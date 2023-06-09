import sys
from djoser.serializers import TokenCreateSerializer, UserSerializer, UserCreateSerializer
from rest_framework.fields import SerializerMethodField
from rest_framework import serializers

from recipes.models import Subscription
from users.models import User


class CustomUserSerializer(UserSerializer):

    def is_sub(self, instance):
        user = self.context['request'].user
        author = instance.id
        try:
            return user.subscriber.filter(author=author).exists()
        except Exception:
            return False

    is_subscribed = SerializerMethodField(method_name='is_sub')

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "id",
            "first_name",
            "last_name",
            "is_subscribed"
        )


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )

# class CustomTokenCreateSerializer(TokenCreateSerializer):

#     class Meta:
#         model = User
#         fields = (
#             "email",
#             "password",
#         )
