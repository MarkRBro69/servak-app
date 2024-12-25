from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    objects = models.Manager()


class Subscription(models.Model):
    follower = models.ForeignKey(Profile, related_name='subscriptions', on_delete=models.CASCADE)
    followed = models.ForeignKey(Profile, related_name='subscribers', on_delete=models.CASCADE)

    objects = models.Manager()
