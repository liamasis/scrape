from rest_framework import serializers
from .models import Session, InstagramAccount, Media

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

class InstagramAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramAccount
        fields = '__all__'

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'
