import re

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import simplejson
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point
from django.db.models import Q

from models import Place, Postcode, Road, Station
from utils import render, is_valid_postcode

def home(request):
    return render(request, 'home.html')

def search(request, type=None):
    q = request.GET.get('q')
    if not q:
        return HttpResponseRedirect('/')

    postcode = lookup_postcode(q)
    if postcode:
        return HttpResponseRedirect('/postcode/%s' % postcode.name)

    latlon = reverse_geocode(q)
    if latlon:
        return HttpResponseRedirect('/point/%s' % latlon)

    map = {}
    places = lookup_places(q)
    if places:
        map['yellow'] = []
        for p in places:
            map['yellow'].append(p.location)
    roads = lookup_roads(q)
    if roads:
        map['red'] = []
        for r in roads:
            if len(map['red']) < 80 - len(map.get('yellow', [])):
                map['red'].append(r.centre)

    for colour, points in map.items():
        if len(points) > 80:
            map[colour] = points[:80]

    return render(request, 'result.html', {
        'q': request.GET.get('q'),
        'places': places,
        'roads': roads,
        'map': map,
    })

def postcode(request, postcode, type=None):
    postcode = lookup_postcode(postcode)
    if not postcode:
        raise Http404

    area = (postcode.location, Distance(mi=1))
    closest = {
        'place': Place.objects.filter(location__dwithin=area).distance(postcode.location).order_by('distance')[:1],
        'road': Road.objects.filter(centre__dwithin=area).distance(postcode.location).order_by('distance')[:1],
    }
    map = {
        'blue': [ postcode.location ],
    }

    if 'application/json' in request.META.get('HTTP_ACCEPT', '') or type == 'json':
        return HttpResponse(simplejson.dumps({
            'postcode': '%s' % postcode,
            'latitude': '%.6f' % postcode.location[1],
            'longitude': '%.6f' % postcode.location[0],
        }), mimetype='application/json')

    return render(request, 'result.html', {
        'q': postcode,
        'postcode': postcode,
        'closest': closest,
        'map': map,
    })

def point(request, lat, lon, type=None):
    lat = float(lat)
    lon = float(lon)
    point = Point(lon, lat, srid=4326)
    area = (point, Distance(mi=1))
    latlon = {
        'postcode': Postcode.objects.filter(location__dwithin=area).distance(point).order_by('distance')[:1],
        'place': Place.objects.filter(location__dwithin=area).distance(point).order_by('distance')[:1],
        'road': Road.objects.filter(centre__dwithin=area).distance(point).order_by('distance')[:1],
    }
    map = {
        'blue': [ point ],
    }

    if 'application/json' in request.META.get('HTTP_ACCEPT', '') or type == 'json':
        out = {}
        for p in ('postcode', 'place', 'road'):
            if latlon[p]:
                out[p] = [ '%s' % latlon[p][0], '%.0f' % latlon[p][0].distance.m ]
        return HttpResponse(simplejson.dumps(out), mimetype='application/json')

    return render(request, 'result.html', {
        'q': '%s,%s' % (lat, lon),
        'latlon': latlon,
        'map': map,
    })

def nearest_station(request, lat, lon, type=None):
    lat = float(lat)
    lon = float(lon)
    point = Point(lon, lat, srid=4326)
    try:
        num = int(request.GET['n'])
        if num > 5: num = 5
        if num < 1: num = 1
    except:
        num = 1
    stations = Station.objects.distance(point).order_by('distance')[:num]
    for station in stations:
        station.location.transform(4326)

    map = {
        'blue': [ point ],
        'yellow': [ station.location for station in stations ],
    }

    if 'application/json' in request.META.get('HTTP_ACCEPT', '') or type == 'json':
        response = HttpResponse(simplejson.dumps([ {
            'station': station.name,
            'code': station.code,
            'latitude': '%.6f' % station.location[1],
            'longitude': '%.6f' % station.location[0],
        } for station in stations ]), mimetype='application/json')
        response['Access-Control-Allow-Origin'] = 'http://traintimes.org.uk'
        return response

    return render(request, 'result.html', {
        'q': '%s,%s' % (lat, lon),
        'stations': stations,
        'map': map,
    })

def furthest_station(request, lat, lon, type=None):
    lat = float(lat)
    lon = float(lon)
    point = Point(lon, lat, srid=4326)
    station = Station.objects.distance(point).order_by('-distance')[0]
    station.location.transform(4326)
    map = {
        'blue': [ point ],
        'yellow': [ station.location ],
    }

    if 'application/json' in request.META.get('HTTP_ACCEPT', '') or type == 'json':
        response = HttpResponse(simplejson.dumps({
            'station': station.name,
            'code': station.code,
            'latitude': '%.6f' % station.location[1],
            'longitude': '%.6f' % station.location[0],
        }), mimetype='application/json')
        response['Access-Control-Allow-Origin'] = 'http://traintimes.org.uk'
        return response

    return render(request, 'result.html', {
        'q': '%s,%s' % (lat, lon),
        'station': station,
        'map': map,
    })

# Lookups

def reverse_geocode(string):
    if not re.match('\s*[0-9.+-]+\s*,\s*[0-9.+-]+\s*$', string):
        return None
    return re.sub('\s+', '', string)

def lookup_postcode(postcode):
    postcode = re.sub('[^A-Z0-9]', '', postcode.upper())
    if not is_valid_postcode(postcode):
        return None
    try:
        postcode = Postcode.objects.get(name=postcode)
        postcode.location.transform(4326)
    except:
        postcode = None
    return postcode

def lookup_places(q):
    places = Place.objects.filter(name__icontains=q).transform()
    return places

def lookup_roads(road):
    road = road.upper()
    if re.match('[ABM]\d+', road):
        roads = Road.objects.filter(Q(number=road) | Q(number='%s(M)' % road)).transform()
    else:
        roads = Road.objects.filter(Q(name__icontains=road)).transform()
    return roads
