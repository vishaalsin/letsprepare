from django.db import models
from django.core.validators import RegexValidator
from yaksh.models import Quiz
from django.contrib.auth.models import User


class Error(models.Model):
    question_id = models.IntegerField("question_id")
    module_id = models.IntegerField("question_id")
    course_id = models.IntegerField("question_id")
    error = models.CharField(max_length=1000, default='TRIAL')

class AvailableQuizzes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, default='TRIAL')
