from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.ProfileListView.as_view(), name='profile-list-view'),
    path('follow/', views.follow_unfollow_profile, name='follow-unfollow-view'),
    path('<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail-view'),
    path('public-profile/<str:username>/', views.public_profile, name='public-profile'),
    path('application/review/<int:applicant_id>/', views.ApplicationReviewView.as_view(), name='application-review'),
    path('mentor_application/<int:pk>/', views.MentorApplicationView.as_view(), name='mentor_application'),
]