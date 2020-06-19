from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from letsprepare.serializers import examSerializer
from yaksh.decorators import has_profile
from yaksh.models import QuestionPaper
from yaksh.views import my_render_to_response
from .models import Exams

class examCrud(APIView):
    @login_required
    @has_profile
    def get(self, request):
        exams = Exams.objects.all()
        exam_serializer = examSerializer(exams, many=True)
        return JsonResponse(exam_serializer.data, status=status.HTTP_200_OK, safe=False)

    @login_required
    @has_profile
    def post(self, request):
        exam_data = JSONParser().parse(request)
        exam_serializer = examSerializer(data=exam_data)
        if exam_serializer.is_valid():
            exam_serializer.save()
            return JsonResponse(exam_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(exam_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @login_required
    @has_profile
    def delete(request, exam_pk):
        exam = Exams.objects.get(pk=exam_pk)
        exam_serializer = examSerializer(exam, many=True)
        return JsonResponse(exam_serializer.data, status=status.HTTP_200_OK)

@login_required
@has_profile
def show_all_quizzes(request):
    user = request.user
    id = request.GET['id']
    exam = list(Exams.objects.filter(id=id))[0]
    question_papers = QuestionPaper.objects.filter(exam=exam.id)
    modules = []
    for qp in question_papers:
        modules.append({
            'name': qp.name,
            'id': qp.id
        })
    context = {
        'course' : exam.exam_name,
        'user': user,
        'modules': modules
    }
    return render(request, 'yaksh/all_quizes.html', context)

@login_required
@has_profile
def show_all_exams(request):
    user = request.user
    # exams = Exams.objects.all()
    courses_data = []
    for exam in list(Exams.objects.all()):
        courses_data.append({'name' : exam.exam_name, 'id' : exam.id})
    context = {
        'user': user, 'courses': courses_data,
        'title': 'ALL AVAILABLE EXAMS'
    }
    return my_render_to_response(request, "yaksh/all_exams.html", context)