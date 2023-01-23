from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login", LoginView.as_view(template_name="login.html")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("form.urls")),
]
