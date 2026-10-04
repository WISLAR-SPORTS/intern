from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from dashboard import views




urlpatterns = [

   
    path('admin/', admin.site.urls),
     path(
        "students/",
        include("students.urls")
    ),
    path("", include("accounts.urls")),
     path(
        "",
        views.intro,
        name="intro"
    ),
     path("companies/", include("companies.urls")),

    
    path(
        "dashboard/",
        include("dashboard.urls"),
    ),

     path("internships/", include("internships.urls")),
path(
        "ai/",
        include("ai_assistant.urls"),
    ),
    

]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )




