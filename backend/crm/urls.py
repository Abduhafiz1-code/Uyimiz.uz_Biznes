from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('clients', views.ClientViewSet, basename='client')
router.register('properties', views.PropertyViewSet, basename='property')
router.register('deals', views.DealViewSet, basename='deal')
router.register('showings', views.ShowingViewSet, basename='showing')
router.register('activities', views.ActivityViewSet, basename='activity')

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('rating/', views.rating_view, name='rating'),
    path('clients/<int:pk>/status/', views.client_status_view, name='client-status'),
    path('', include(router.urls)),
]
