from django.conf.urls import url

from imageresize.main.views import health_view, ResizeViewSet

urlpatterns = [
    url(r'^health/', health_view),
    url(r'^thumb', ResizeViewSet.as_view()),
]
