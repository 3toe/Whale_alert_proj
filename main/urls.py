from django.urls import path     
from . import views

urlpatterns = [
   # GET method to render the login page
   path('', views.index),
   # POST method for the registration
   path('reg', views.reg),
   # POST method for the login
   path('login', views.login),
   # GET method logging the user out
   path('logout', views.logout),
   # other shits
]