from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
#from django.db.models import Value
#from django.db.models.functions import Concat
#from django.utils.html import escape

from agencies.models import RegisteredAgency, Applications, ApplicationStandard, EsgStandard

import csv

class Command(BaseCommand):
    help = 'Import ApplicationStandard data'

    def add_arguments(self, parser):
        parser.add_argument('file',
                            help = 'CSV file to import')
        parser.add_argument('-n', '--dry-run', action='store_true',
                            help = 'parse file only without saving data')

    def handle(self, *args, **options):

        with open(options['file'], newline='', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)

            for lineno, data in enumerate(reader, start=2):
                try:
                    application = Applications.objects.get(agency__shortname=data['agency'], decisionDate__year=data['year'])
                except Applications.DoesNotExist:
                    print(f"line {lineno} - Application not found: agency={data['agency']} year={data['year']}")
                except Applications.MultipleObjectsReturned:
                    print(f"line {lineno} - Application is not unique defined by: agency={data['agency']} year={data['year']}")
                else:
                    try:
                        standard = EsgStandard.objects.get(version__active=True, part=data['part'], number=data['standard'])
                    except EsgStandard.DoesNotExist:
                        print(f"line {lineno} - Standard not found: ESG {data['part']}.{data['standard']}")
                    else:
                        ApplicationStandard.objects.update_or_create(
                            application=application,
                            standard=standard,
                            defaults=dict(
                                keywords=data['keywords'],
                                decision=data['decision']
                            )
                        )

