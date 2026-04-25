from django.urls import path

from .views import timeline_view


app_name = "lifegraph"

urlpatterns = [
    path("", timeline_view, name="timeline"),
]
