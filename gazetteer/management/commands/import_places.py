import sys
import csv

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from gazetteer.models import Place

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0

        for row in csv.reader(sys.stdin, delimiter=':'):
            args = {
                'name': row[2].decode('iso-8859-1').strip().replace('  ', ' '),
                'tile_ref': row[1],
                'location': Point(float(row[9]), float(row[8])),
                'county': row[11],
                'type': row[14],
                'os_map': ','.join(row[17:20]),
            }
            if not Place.objects.filter(**args).count():
                Place.objects.create(**args)

            count += 1
            if count % 10000 == 0:
                print "Imported %d" % count

