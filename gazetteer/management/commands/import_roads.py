import sys
import csv

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from gazetteer.models import Road

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0

        for row in csv.reader(sys.stdin, delimiter=':'):
            args = {
                'name': row[0].decode('iso-8859-1'),
                'number': row[1],
                'centre': Point(map(float, row[2:4])),
                'min': Point(float(row[4]), float(row[6])),
                'max': Point(float(row[5]), float(row[7])),
                'settlement': row[8].decode('iso-8859-1'),
                'locality': row[9].decode('iso-8859-1'),
                'county': row[10].decode('iso-8859-1'),
                'council': row[11].decode('iso-8859-1'),
                'tile10k': row[12],
                'tile25k': row[13],
            }
            Road.objects.get_or_create(**args)

            count += 1
            if count % 10000 == 0:
                print "Imported %d" % count

