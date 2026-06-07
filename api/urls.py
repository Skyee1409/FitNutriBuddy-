from django.urls import path
from .views import ChatView, GeneratePlanView, GenerateAllPlansView, HealthCheckView

urlpatterns = [
    path('chat/',           ChatView.as_view(),           name='api-chat'),
    path('generate-plan/',  GeneratePlanView.as_view(),   name='api-generate-plan'),
    path('generate-all/',   GenerateAllPlansView.as_view(),name='api-generate-all'),
    path('health/',         HealthCheckView.as_view(),    name='api-health'),
]
