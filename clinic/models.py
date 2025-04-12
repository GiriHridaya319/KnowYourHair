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
    image = models.ImageField(upload_to='clinics_images/', default='default.jpg',)
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


class Dermatologist(models.Model):

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    About = models.TextField()
    image = models.ImageField(upload_to='dermatologist_images/', default='default.jpg')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="dermatologists")
    phoneNum = models.CharField(max_length=100)
    total_experience = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} - {self.last_name}"

    def get_absolute_url(self):
        return reverse('dermatologist-detail', kwargs={'pk': self.pk})


class BookingClinic(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dermatologist = models.ForeignKey(Dermatologist, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    appointment_time = models.DateTimeField()
    country = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        default='pending'
    )
    message = models.TextField(blank=True, null=True)
    hair_report_pdf = models.FileField(upload_to='hair_reports/', blank=True, null=True)  # New field for PDF upload

    def __str__(self):
        return f"Appointment with {self.dermatologist.first_name} on {self.appointment_time} in {self.clinic}"

    def is_today(self):
        return self.appointment_time.date() == timezone.now().date()

    def is_upcoming(self):
        return self.appointment_time > timezone.now()

    # Add a method to check if the file exists
    def has_hair_report(self):
        return bool(self.hair_report_pdf)
