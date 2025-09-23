from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("demo/panel", views.panel, name="panel"),
]
