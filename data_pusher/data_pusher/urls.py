from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from core.views import IncomingDataView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/token-auth/", obtain_auth_token, name="token-auth"),
    path("api/server/incoming-data/", IncomingDataView.as_view(), name="incoming-data"),
]
