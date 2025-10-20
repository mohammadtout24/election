from django.urls import path
from . import views

# Define the app_name in your project urls.py or here if this is the app's urls.py
# app_name = 'candidates' 

urlpatterns = [
    # Public views
    # The root of the app should probably be the public home page for the election
    path('', views.home, name='home'), 
    path('candidate/<int:candidate_id>/', views.candidate_detail, name='candidate_detail'),
    
    # Auth views
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Voting functionality
    path('vote/', views.submit_vote, name='submit_vote'), 
    
   
]
