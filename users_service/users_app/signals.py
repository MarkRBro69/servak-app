from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from users_app.models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        profile = Profile.objects.get(user=instance)
    except Profile.DoesNotExist:
        profile = None

    if profile is not None:
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)
