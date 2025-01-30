from django.db.models.signals import post_save
from django.contrib.auth.models import User  # user is the sender as it is sending
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)  # when a user is saved, send this signal
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)  # when a user is saved, send this signal
def save_profile(sender, instance, **kwargs):  # kwargs is for any additional arguments
    instance.profile.save()
