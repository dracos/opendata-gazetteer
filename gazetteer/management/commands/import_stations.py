import sys
import csv

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from gazetteer.models import Station

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0

# "AtcoCode","TiplocCode","CrsCode","StationName","StationNameLang","GridType","Easting","Northing"
        fp = csv.reader(sys.stdin)
        fp.next() # header row
        for row in fp:
            args = {
                'name': row[3].strip(),
                'code': row[2].strip(),
                'location': Point(map(float, row[6:8])),
            }
            Station.objects.get_or_create(**args)

            count += 1
            if count % 1000 == 0:
                print "Imported %d" % count

