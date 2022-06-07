from django.urls import path, include
from rest_framework import routers

from main import viewsets, views


router = routers.SimpleRouter(trailing_slash=False)
router.register('', viewsets.CacheViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.index, name='index'),
]
