from django.contrib import admin
from .models import Exams
admin.site.site_header = ""


class ExamModelAdmin(admin.ModelAdmin):
    list_display = ["exam_name"]


admin.site.register(Exams, ExamModelAdmin)


