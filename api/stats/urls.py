from django.urls import path, include

from stats.views import *

class UrlList(list):

    def add_url(self, url, view):
        self.append(path(f'{url}/', view.as_view()))
        self.append(path(f'{url}.<slug:format>/', view.as_view()))

urlpatterns = UrlList()
urlpatterns.add_url(r'esg/simple', ComplianceStats)
urlpatterns.add_url(r'esg/extended', ComplianceExtendedStats)
urlpatterns.add_url(r'applications/open', OpenApplications)
urlpatterns.add_url(r'applications/withdrawn', WithdrawnApplications)
urlpatterns.add_url(r'applications/by-year', ApplicationsTimeline)

