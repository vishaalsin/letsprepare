from django.db import models

class Exams(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    exam_name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.exam_name)

