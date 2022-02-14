from django.urls import path, include

from stats.views import *

urlpatterns = [
    path(r'esg/simple/', ComplianceStats.as_view()),
    path(r'esg/extended/', ComplianceExtendedStats.as_view()),
    path(r'applications/open/', OpenApplications.as_view()),
    path(r'applications/withdrawn/', WithdrawnApplications.as_view()),
    path(r'applications/by-year/', ApplicationsTimeline.as_view()),
]


