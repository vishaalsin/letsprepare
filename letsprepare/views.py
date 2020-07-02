from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from yaksh.decorators import has_profile
from yaksh.models import QuestionPaper, AnswerPaper
from yaksh.models import LearningModule
from yaksh.views import my_render_to_response
from rest_framework import status
from letsprepare.models import AvailableQuizzes
from letsprepare.serializers import AvailableQuizzesSerializer, ErrorSerializer
import json
from plotly.offline import plot
import plotly.graph_objs as go

@login_required
@has_profile
def show_all_quizzes(request):
    user = request.user
    id = request.GET['id']
    availableQuizzes = json.loads(json.dumps(AvailableQuizzesSerializer(AvailableQuizzes.objects.filter(user=user), many=True).data))
    availableQuizIds = [quiz['quiz'] for quiz in availableQuizzes]
    module = LearningModule.objects.get(id = id)
    quizzes = module.get_quiz_units()
    answerpapers = AnswerPaper.objects.filter(user=request.user)
    question_papers_attempted = [i.question_paper.id for i in answerpapers]
    question_papers_data = []
    for qz in quizzes:
        for qp in list(QuestionPaper.objects.filter(quiz=qz.id)):
            question_papers_data.append({
                'code' : qz.quiz_code,
                'name': qz.description,
                'id': qp.id,
                'attempts' : question_papers_attempted.count(qp.id)
            })
            if qz.id in availableQuizIds:
                question_papers_data[-1]['available'] = True
            else:
                question_papers_data[-1]['available'] = False

    context = {
        'module' : module.name,
        'module_id' : module.id,
        'user': user,
        'question_papers': question_papers_data
    }
    return render(request, 'yaksh/all_question_papers.html', context)

@login_required
@has_profile
def show_all_modules(request):
    user = request.user
    # exams = Exams.objects.all()
    modules_data = []
    availableQuizzes = json.loads(json.dumps(AvailableQuizzesSerializer(AvailableQuizzes.objects.filter(user=user), many=True).data))
    availableQuizIds = [quiz['quiz'] for quiz in availableQuizzes]
    for module in list(LearningModule.objects.all()):
        quizzes = [quiz.id for quiz in module.get_quiz_units()]
        has_quizzes = 0
        for quiz_id in quizzes:
            if quiz_id in availableQuizIds:
                has_quizzes += 1
        modules_data.append({'name' : module.description, 'id' : module.id,
                              'total_quizzes' : len(quizzes), 'has_quizzes' : has_quizzes })
    context = {
        'user': user, 'modules': modules_data,
        'title': 'ALL  AVAILABLE  MODULES'
    }
    return my_render_to_response(request, "yaksh/all_modules.html", context)

@login_required
@has_profile
def show_all_on_sale(request):
    user = request.user
    modules_data = []
    for module in list(LearningModule.objects.all()):
        quizzes = module.get_quiz_units()
        quiz_data = []
        for quiz in list(quizzes):
            quiz_data.append({'name': quiz.description, 'code' : quiz.quiz_code, 'price' : quiz.price, 'id':quiz.id})
        modules_data.append({'name': module.description, 'id': module.id, 'quizzes': quiz_data, 'state': 'Active'})

    context = {
        'user': user, 'modules': modules_data,
        'title': 'ALL  AVAILABLE  MODULES'
    }
    return my_render_to_response(request, "yaksh/all_on_sale.html", context)

@csrf_exempt
@login_required
@has_profile
def assign_quizzes(request):
    results = json.loads(request.POST['data'])

    try:
        for quiz in results['quizzes']:
            data = {'user' : request.user.id,
                    'quiz' : quiz
                    }
            available_quizzes_serializer = AvailableQuizzesSerializer(data=data)
            if available_quizzes_serializer.is_valid():
                available_quizzes_serializer.save()

        return JsonResponse({'SUCCESS': 'Thanks for buying!!'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return JsonResponse(str(e), status=status.HTTP_400_BAD_REQUEST)

@login_required
def show_results(request):
    answerpapers = AnswerPaper.objects.filter(user = request.user)
    question_papers_attempted = [i.question_paper for i in answerpapers]
    question_papers_data = []
    for qp in set(question_papers_attempted):
        question_papers_data.append({
            'code' : qp.quiz.quiz_code,
            'name': qp.quiz.description,
            'id': qp.id
        })
    fig = get_percentage_graph(question_papers_attempted,answerpapers)
    plot_div = plot(fig,
        output_type='div',config=dict(
                    displayModeBar=False,
                    dragMode=False,
                    scrollZoom=False,
                    staticPlot= True
                ), include_plotlyjs=False)
    fig2 = get_accuracy_graph(question_papers_attempted, answerpapers)
    plot_div2 = plot(fig2,
                    output_type='div', config=dict(
            displayModeBar=False,
            dragMode=False,
            scrollZoom=False,
            staticPlot=True
        ), include_plotlyjs=False)
    return my_render_to_response(request, "yaksh/results.html", context={'question_papers' : question_papers_data, 'plot_div': plot_div, 'plot_div2': plot_div2})


def get_accuracy_graph(question_papers_attempted, answerpapers):
    attempt_dict = {}
    qa_tups = zip(question_papers_attempted,answerpapers)
    qa_tups_ordered = [qa for qa in sorted(qa_tups, key=lambda item: item[1].end_time)]
    for qp, ap in qa_tups_ordered:
        if qp.quiz.quiz_code in attempt_dict.keys():
            attempt_dict[qp.quiz.quiz_code].append(round(((ap.marks_obtained)/len(ap.questions_answered.all())*100),2))
        else:
            attempt_dict[qp.quiz.quiz_code] = []
            attempt_dict[qp.quiz.quiz_code].append(round(((ap.marks_obtained)/len(ap.questions_answered.all()))*100,2))

    fy = []
    sy = []

    attempts = list(attempt_dict.keys())
    for uqp in attempts:
        try:
            fy.append(attempt_dict[uqp][0])
        except:
            fy.append(0)
        try:
            sy.append(attempt_dict[uqp][1])
        except:
            sy.append(0)

    trace1 = go.Bar(
        x=attempts,
        y=fy,
        text=[str(i) for i in fy],
        textposition='outside',
        name='Attempt 1',
        hoverinfo='skip'
    )
    trace2 = go.Bar(
        x=attempts,
        y=sy,
        text=[str(i) for i in sy],
        textposition='outside',
        name='Attempt 2',
        hoverinfo='skip'
    )

    data = [trace1, trace2]
    layout = go.Layout(barmode='group', yaxis=dict(range=[0, 108]))
    fig = go.Figure(data=data, layout=layout)
    return fig


def get_percentage_graph(question_papers_attempted, answerpapers):
    attempt_dict = {}
    qa_tups = zip(question_papers_attempted,answerpapers)
    qa_tups_ordered = [qa for qa in sorted(qa_tups, key=lambda item: item[1].end_time)]
    for qp, ap in qa_tups_ordered:
        if qp.quiz.quiz_code in attempt_dict.keys():
            attempt_dict[qp.quiz.quiz_code].append(ap.percent)
        else:
            attempt_dict[qp.quiz.quiz_code] = []
            attempt_dict[qp.quiz.quiz_code].append(ap.percent)

    fy = []
    sy = []

    attempts = list(attempt_dict.keys())
    for uqp in attempts:
        try:
            fy.append(attempt_dict[uqp][0])
        except:
            fy.append(0)
        try:
            sy.append(attempt_dict[uqp][1])
        except:
            sy.append(0)

    trace1 = go.Bar(
        x=attempts,
        y=fy,
        text=[str(i) for i in fy],
        textposition='outside',
        name='Attempt 1',
        hoverinfo='skip'
    )
    trace2 = go.Bar(
        x=attempts,
        y=sy,
        text=[str(i) for i in sy],
        textposition='outside',
        name='Attempt 2',
        hoverinfo='skip'
    )

    data = [trace1, trace2]
    layout = go.Layout(barmode='group', yaxis=dict(range=[0, 108]))
    fig = go.Figure(data=data, layout=layout)
    return fig

@csrf_exempt
@login_required
@has_profile
def report_error(request):
    data = json.loads(request.POST['data'])
    try:
        error_serializer = ErrorSerializer(data=data)
        if error_serializer.is_valid():
            error_serializer.save()

        return JsonResponse({'SUCCESS': 'Thanks for buying!!'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return JsonResponse(str(e), status=status.HTTP_400_BAD_REQUEST)