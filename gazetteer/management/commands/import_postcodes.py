import sys
import csv

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from gazetteer.models import Postcode

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0

        for row in csv.reader(sys.stdin):
            args = {
                'name': row[0].strip().replace(' ', ''),
                'location': Point(map(float, row[10:12])),
            }
            Postcode.objects.get_or_create(**args)

            count += 1
            if count % 10000 == 0:
                print "Imported %d" % count

