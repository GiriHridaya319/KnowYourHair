from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from PIL import Image


class Clinic(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='clinics_images/', blank=True, null=True)
    address = models.CharField(max_length=100)
    opening_time = models.CharField(max_length=100)
    closing_time = models.CharField(max_length=100)
    phoneNum = models.CharField(max_length=100)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.name} - {self.status}"

    def get_absolute_url(self):
        return reverse('clinic-detail', kwargs={'pk': self.pk})

# Create your models here.

    def save(self):
        super().save()  # run the save method of the parent class
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
