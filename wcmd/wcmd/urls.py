#from django.conf.urls import patterns, url, include
from django.urls import path #, re_path #, include 
#from django.views.generic import RedirectView
from wcmd.wcmd.views import *
#from django.contrib.auth.decorators import login_required, permission_required
#from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', AgencyList.as_view(), name='agency_list'),
    path('<slug:slug>/', AgencyDetail.as_view(), name='agency_detail'),
    path('<slug:slug>/edit/', AgencyEditView.as_view(), name='agency_edit'),
    path('<slug:slug>/measure/', AgencyMeasuresEditView.as_view(), name='agency_measures_edit'),
    #path('<slug:aslug>/measure/', agency_measures_edit, name='agency_measures_edit'),
    path('<slug:aslug>/measure/add/', AgencyMeasureAddView.as_view(), name='agency_measure_add'),
    path('<slug:aslug>/measure/<slug:mslug>/', agency_measure_detail, name='agency_measure_detail'),
    path('<slug:aslug>/measure/<slug:mslug>/edit/', AgencyMeasureEditView.as_view(), name='agency_measure_edit'),
    path('<slug:aslug>/<slug:wslug>/', wilderness_detail, name='wilderness_detail'),
    path('<slug:aslug>/<slug:wslug>/edit/', WildernessEditView.as_view(), name='wilderness_edit'),
    path('<slug:aslug>/<slug:wslug>/measure/', wilderness_measures_edit, name='wilderness_measures_edit'),
    path('<slug:aslug>/<slug:wslug>/measure/<slug:mslug>/', wilderness_measure_detail, name='wilderness_measure_detail'),
    path('<slug:aslug>/<slug:wslug>/<int:year>/', trendreport_detail, name='trendreport_detail'),
    path('<slug:aslug>/<slug:wslug>/<int:year>/edit/', trendreport_edit, name='trendreport_edit'),
    path('<slug:aslug>/<slug:wslug>/<int:year>/measure/<slug:mslug>/', trendreport_measure_detail, name='trendreport_measure_detail'),
    path('<slug:aslug>/<slug:wslug>/<int:year>/measure/<slug:mslug>/edit/', trendreport_measure_edit, name='trendreport_measure_edit'),
]
