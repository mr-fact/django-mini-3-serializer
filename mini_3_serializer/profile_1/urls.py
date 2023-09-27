from django.urls import path
from rest_framework.routers import DefaultRouter

from profile_1.views import UserHyperLinkViewSet

router = DefaultRouter()
router.register('test5', UserHyperLinkViewSet, )

urlpatterns = [

] + router.urls
