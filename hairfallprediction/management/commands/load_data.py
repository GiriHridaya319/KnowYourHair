from django.core.management.base import BaseCommand
import pandas as pd
from hairfallprediction.models import HairfallData, Product


class Command(BaseCommand):
    help = 'Load data from CSV files into database'

    def handle(self, *args, **kwargs):
        # Load hairfall dataset
        hairfall_df = pd.read_csv('hairfallprediction/data/hairfall_dataset.csv')
        self.stdout.write('Loading hairfall data...')

        for _, row in hairfall_df.iterrows():
            HairfallData.objects.create(
                gender=row['Gender'],
                age=row['Age'],
                hairline_pattern=row['Hairline Pattern'],
                hair_fall_rate=row['Hair Fall Rate'],
                nutrition=row['Nutrition'],
                chemical_product_usage=row['Chemical Product Usage'],
                genetics=row['Genetics'],
                past_chronic_illness=row['Past Chronic Illness'],
                sleep_disturbance=row['Sleep Disturbance'],
                water_quality_issue=row['Water Quality Issue'],
                stress=row['Stress'],
                food_habit=row['Food Habit'],
                hormonal_changes=row['Hormonal Changes'],
                hair_care_habits=row['Hair Care Habits'],
                smoking=row['Smoking'],
                label=row['Label']
            )

        # Load products dataset
        products_df = pd.read_csv('hairfallprediction/data/products.csv')
        self.stdout.write('Loading products data...')

        for _, row in products_df.iterrows():
            Product.objects.create(
                name=row['ProductsName'],
                cost=row['Product Cost'],
                feedback=row['Feedbacks'],
                details=row['Details']
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded all data'))