from django.urls import path, include

from stats.views import *

class UrlList(list):

    def add_url(self, url, view):
        self.append(path(f'{url}/', view.as_view()))
        self.append(path(f'{url}.<slug:format>/', view.as_view()))

urlpatterns = UrlList()
urlpatterns.add_url(r'esg/simple', ComplianceStats)
urlpatterns.add_url(r'esg/extended', ComplianceExtendedStats)
urlpatterns.add_url(r'esg/timeline-by-standard', ComplianceTimelineByStandard)
urlpatterns.add_url(r'esg/compliance-changed/by-year', ComplianceChangeStats)
urlpatterns.add_url(r'esg/compliance-changed/by-standard', ComplianceChangePerStandardStats)
urlpatterns.add_url(r'esg/compliance-changed/by-panel', ComplianceChangePerPanelStats)
urlpatterns.add_url(r'esg/compliance-changed/by-rapporteur', ComplianceChangePerRapporteurStats)

urlpatterns.add_url(r'applications/open', OpenApplications)
urlpatterns.add_url(r'applications/withdrawn', WithdrawnApplications)
urlpatterns.add_url(r'applications/by-year', ApplicationsTimeline)
urlpatterns.add_url(r'applications/totals', ApplicationsTotals)
urlpatterns.add_url(r'applications/duration/latest', ApplicationsDuration)
urlpatterns.add_url(r'applications/duration/by-year', ApplicationsDurationPerYear)
urlpatterns.add_url(r'applications/precedents', ApplicationPrecedentList)
urlpatterns.add_url(r'applications/clarification-requests', ClarificationRequestStats)

