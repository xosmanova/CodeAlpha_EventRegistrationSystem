from django.urls import path
from . import api_views
from . import web_views

urlpatterns = [
    # Web UI Views
    path('', web_views.home, name='home'),
    path('events/<int:pk>/', web_views.event_detail, name='event_detail'),
    path('events/create/', web_views.create_event, name='create_event'),
    path('my-registrations/', web_views.my_registrations, name='my_registrations'),
    path('registrations/<int:pk>/cancel/', web_views.cancel_registration, name='cancel_registration'),
    path('docs/', web_views.api_documentation_view, name='api_docs'),
    path('login/', web_views.user_login, name='login'),
    path('signup/', web_views.user_signup, name='signup'),
    path('logout/', web_views.user_logout, name='logout'),

    # REST API - Authentication
    path('api/auth/register/', api_views.AuthRegisterView.as_view(), name='api_register'),
    path('api/auth/login/', api_views.AuthLoginView.as_view(), name='api_login'),
    path('api/auth/logout/', api_views.AuthLogoutView.as_view(), name='api_logout'),
    path('api/auth/me/', api_views.AuthCurrentUserView.as_view(), name='api_current_user'),

    # REST API - Events
    path('api/events/', api_views.EventListCreateAPIView.as_view(), name='api_events_list'),
    path('api/events/<int:pk>/', api_views.EventDetailAPIView.as_view(), name='api_event_detail'),
    path('api/events/<int:event_id>/register/', api_views.RegistrationCreateAPIView.as_view(), name='api_event_register'),
    path('api/events/<int:event_id>/attendees/', api_views.EventAttendeesAPIView.as_view(), name='api_event_attendees'),

    # REST API - Registrations
    path('api/registrations/', api_views.RegistrationCreateAPIView.as_view(), name='api_registrations'),
    path('api/my-registrations/', api_views.MyRegistrationsAPIView.as_view(), name='api_my_registrations'),
    path('api/registrations/<int:pk>/cancel/', api_views.RegistrationCancelAPIView.as_view(), name='api_registration_cancel'),
    path('api/registrations/<int:pk>/', api_views.RegistrationCancelAPIView.as_view(), name='api_registration_detail'),
]
