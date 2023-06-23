import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def import_ingredients(model):
    with open(os.path.join(settings.BASE_DIR, 'data/ingredients.csv')) as f:
        reader = csv.reader(f)
        for row in reader:
            _, created = model.objects.get_or_create(
                name=row[0].lower(), measurement_unit=row[1].lower())


def clear_ingredients(model):
    model.objects.all().delete()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--add",
            action="store_true",
        )
        parser.add_argument(
            "--delete",
            action="store_true",
        )

    def handle(self, *args, **options):
        if options["add"]:
            import_ingredients(Ingredient)
        if options["delete"]:
            clear_ingredients(Ingredient)
