from django.conf.urls.defaults import *

urlpatterns = patterns('gazetteer.views',
    (r'^$', 'home'),
    (r'^search$', 'search'),
    (r'^postcode/(?P<postcode>.*?)(?:\.(?P<type>json))?$', 'postcode'),
    (r'^point/(?P<lat>.*?),(?P<lon>.*?)(?:\.(?P<type>json))?$', 'point'),
)

