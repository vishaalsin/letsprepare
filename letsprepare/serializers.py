from rest_framework import serializers
from letsprepare.models import AvailableQuizzes, Error

class AvailableQuizzesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableQuizzes
        fields = '__all__'

class ErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Error
        fields = '__all__'