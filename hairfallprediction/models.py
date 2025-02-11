from django.db import models


class HairfallData(models.Model):
    gender = models.IntegerField()
    age = models.IntegerField()
    hairline_pattern = models.IntegerField()
    hair_fall_rate = models.IntegerField()
    nutrition = models.IntegerField()
    chemical_product_usage = models.IntegerField()
    genetics = models.IntegerField()
    past_chronic_illness = models.IntegerField()
    sleep_disturbance = models.IntegerField()
    water_quality_issue = models.IntegerField()
    stress = models.IntegerField()
    food_habit = models.IntegerField()
    hormonal_changes = models.IntegerField()
    hair_care_habits = models.IntegerField()
    smoking = models.IntegerField()
    label = models.IntegerField()  # Risk level label

    class Meta:
        db_table = 'hairfall_data'


class Product(models.Model):
    name = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    feedback = models.TextField()
    details = models.TextField()

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name