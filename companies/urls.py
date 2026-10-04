from django.urls import path
from .views import landing_page, company_dashboard


app_name = "companies"

urlpatterns = [
    path("home/", landing_page, name="landing"),
    
    path(
        "dashboard/",
        company_dashboard,
        name="company_dashboard",
    ),
    

]

