from django.shortcuts import render
from rest_framework import viewsets


# Create your views here.
from djoser.views import UserViewSet

from api.serializers import TagSerializer
from recipes.models import Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
