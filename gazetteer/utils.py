import re

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db import connection

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

