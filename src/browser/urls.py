"""Defines the routing table of the application."""
from browser import views
from django.urls import path

app_name = "browser"
urlpatterns = [path("", views.IndexView.as_view(), name="index")]
