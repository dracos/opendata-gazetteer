import re

from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point
from django.template import RequestContext
from django.db import connection
from django.db.models import Q

from models import Place, Postcode, Road

# Utility functions

def render(request, template_name, context=None):
    if context is None: context = {}
    context['connection'] = connection
    return render_to_response(
        template_name, context, context_instance = RequestContext(request)
    )

def is_valid_postcode(postcode):
    postcode = re.sub('[^A-Z0-9]', '', postcode.upper())
    inw = 'ABDEFGHJLNPQRSTUWXYZ';
    fst = 'ABCDEFGHIJKLMNOPRSTUWYZ';
    sec = 'ABCDEFGHJKLMNOPQRSTUVWXY';
    thd = 'ABCDEFGHJKSTUW';
    fth = 'ABEHMNPRVWXY';
    if re.match('^[%s][1-9]\d[%s][%s]$' % (fst, inw, inw), postcode) \
        or re.match('^[%s][1-9]\d\d[%s][%s]$' % (fst, inw, inw), postcode) \
        or re.match('^[%s][%s]\d\d[%s][%s]$' % (fst, sec, inw, inw), postcode) \
        or re.match('^[%s][%s][1-9]\d\d[%s][%s]$' % (fst, sec, inw, inw), postcode) \
        or re.match('^[%s][1-9][%s]\d[%s][%s]$' % (fst, thd, inw, inw), postcode) \
        or re.match('^[%s][%s][1-9][%s]\d[%s][%s]$' % (fst, sec, fth, inw, inw), postcode):
            return True
    return False

# Main views

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

    if 'application/json' in request.META.get('HTTP_ACCEPT') or type == 'json':
        return HttpResponse(simplejson.dumps({
            'postcode': '%s' % postcode,
            'latitude': round(postcode.location[1], 6),
            'longitude': round(postcode.location[0], 6),
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

    if 'application/json' in request.META.get('HTTP_ACCEPT') or type == 'json':
        return HttpResponse(simplejson.dumps({
            'postcode': '%s' % latlon['postcode'][0],
            'place': '%s' % latlon['place'][0],
            'road': '%s' % latlon['road'][0],
        }), mimetype='application/json')

    return render(request, 'result.html', {
        'q': '%s,%s' % (lat, lon),
        'latlon': latlon,
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
