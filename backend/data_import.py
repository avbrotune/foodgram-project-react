import csv

from recipes.models import Ingredient

path = "/home/avbro/foodgram-project-react/data/ingredients.csv"

with open(path) as f:
    reader = csv.reader(f)
    for row in reader:
        _, created = Ingredient.objects.get_or_create(
            name=row[0].lower(), measurement_unit=row[1].lower())
