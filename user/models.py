from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default_user.jpg', upload_to='profiles/')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)

    @property
    def role(self):
        # Determine user role based on linked profiles
        if hasattr(self, 'agent'):
            return self.agent.role
        elif hasattr(self, 'customer'):
            return self.customer.role
        return None

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
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='agent')
    role = models.CharField(max_length=100, blank=True, null=True, default='staff')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.profile.user.username


class Customer(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='customer')
    role = models.CharField(max_length=100, blank=True, null=True, default='customer')

    def __str__(self):
        return self.profile.user.username