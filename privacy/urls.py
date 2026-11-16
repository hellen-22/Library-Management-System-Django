from django.urls import path
from . import views

urlpatterns = [
    path('', views.page, name='gdpr-page'),
    path('csrf/', views.csrf, name='gdpr-csrf'),
    path('consent/', views.consent, name='gdpr-consent'),
    path('<str:operation>/', views.evaluate, name='gdpr-evaluate'),
]
