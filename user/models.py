from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default_user.jpg' , upload_to='profiles/')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # Check if no image is uploaded and set the default image
        if not self.image:
            self.image = 'profiles/default_user.jpg'
        super().save(*args, **kwargs)  # Call the parent class's save method

        # Resize image if needed
        if self.image and self.image != 'profiles/default_user.jpg':
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)


class Agent(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='agent')
    role = models.CharField(max_length=100, blank=True, null=True, default='staff')  # Renamed from specialization

    def __str__(self):
        return self.profile.user.username


class Customer(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='customer')
    role = models.CharField(max_length=100, blank=True, null=True, default='customer')  # Renamed from preferences

    def __str__(self):
        return self.profile.user.username

