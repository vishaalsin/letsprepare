from rest_framework import serializers
from letsprepare.models import Exams


class examSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exams
        fields = ('id',
                  'exam_name')
