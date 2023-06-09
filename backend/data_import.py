from recipes.models import Ingredient
import csv
path = "/home/avbro/foodgram-project-react/data/ingredients.csv"

with open(path) as f:
    reader = csv.reader(f)
    for row in reader:
        _, created = Ingredient.objects.get_or_create(name=row[0],measurement_unit=row[1])