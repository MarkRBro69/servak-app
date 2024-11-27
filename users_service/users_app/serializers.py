from django.contrib.auth.models import User
from rest_framework import serializers

from users_app.models import Subscription


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class SubscriptionSerializer(serializers.ModelSerializer):
    follower = serializers.SerializerMethodField()
    followed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['follower', 'followed']

    @staticmethod
    def get_follower(obj):
        return {
            "id": obj.follower.id,
            "username": obj.follower.user.username
        }

    @staticmethod
    def get_followed(obj):
        return {
            "id": obj.followed.id,
            "username": obj.followed.user.username
        }
