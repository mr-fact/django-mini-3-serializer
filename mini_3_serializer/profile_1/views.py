from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from profile_1.models import MyUser
from profile_1.serializers import UserHyperLinkSerializer


# test 5
class UserHyperLinkViewSet(ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserHyperLinkSerializer
