from django.conf.urls import patterns

urlpatterns = patterns('gazetteer.views',
    (r'^$', 'home'),
    (r'^search$', 'search'),
    (r'^postcode/(?P<postcode>.*?)(?:\.(?P<type>json))?$', 'postcode'),
    (r'^point/(?P<lat>.*?),(?P<lon>.*?)(?:\.(?P<type>json))?$', 'point'),
    (r'^nearest/station/(?P<lat>.*?),(?P<lon>.*?)(?:\.(?P<type>json))?$', 'nearest_station'),
    (r'^furthest/station/(?P<lat>.*?),(?P<lon>.*?)(?:\.(?P<type>json))?$', 'furthest_station'),
)

