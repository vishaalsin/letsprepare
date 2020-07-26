from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from yaksh.decorators import has_profile
from yaksh.models import QuestionPaper, AnswerPaper, Profile, Course
from yaksh.models import LearningModule, Quiz
from yaksh.views import my_render_to_response, my_redirect
from rest_framework import status
from letsprepare.models import AvailableQuizzes, PaytmHistory
from letsprepare.serializers import AvailableQuizzesSerializer, ErrorSerializer
import json
from plotly.offline import plot
import plotly.graph_objs as go
from twilio.rest import Client
from random import randint
from online_test import settings

import razorpay

if not settings.IS_DEVELOPMENT:
    key = settings.rzp_key_dev
    secret_key = settings.rzp_secret_key_dev
else:
    key = settings.rzp_key_prod
    secret_key = settings.rzp_secret_key_prod

client = razorpay.Client(auth=(key, secret_key))

tw_client = Client(settings.sid, settings.token)

@login_required
@has_profile
def show_all_quizzes(request):
    user = request.user
    id = request.GET['id']
    availableQuizzes = json.loads(json.dumps(AvailableQuizzesSerializer(AvailableQuizzes.objects.filter(user=user, successful=True), many=True).data))
    availableQuizIds = [quiz['quiz'] for quiz in availableQuizzes]
    module = LearningModule.objects.get(id = id)
    course = list(Course.objects.all())[0]
    quizzes = module.get_quiz_units()
    quizzes = sorted(quizzes, key=lambda item: int(item.quiz_code.split('_')[1]))
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
            if qz.id in availableQuizIds or qz.is_free:
                question_papers_data[-1]['available'] = True
            else:
                question_papers_data[-1]['available'] = False

    context = {
        'module' : module.name,
        'module_id' : module.id,
        'course_id' : course.id,
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
    availableQuizzes = json.loads(json.dumps(AvailableQuizzesSerializer(AvailableQuizzes.objects.filter(user=user, successful = True), many=True).data))
    availableQuizIds = [quiz['quiz'] for quiz in availableQuizzes]
    for module in list(LearningModule.objects.all()):
        quizzes = module.get_quiz_units()
        has_quizzes = 0
        for quiz in quizzes:
            if quiz.id in availableQuizIds or quiz.is_free:
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
    availableQuizzes = json.loads(json.dumps(AvailableQuizzesSerializer(AvailableQuizzes.objects.filter(user=user, successful=True), many=True).data))
    availableQuizIds = [quiz['quiz'] for quiz in availableQuizzes]
    for module in list(LearningModule.objects.all()):
        quizzes = module.get_quiz_units()
        quizzes = sorted(quizzes, key=lambda item: int(item.quiz_code.split('_')[1]))
        quiz_data = []
        for quiz in list(quizzes):
            quiz_data.append({'name': quiz.description, 'code' : quiz.quiz_code, 'price' : quiz.price, 'org_price' : quiz.price *2, 'id':quiz.id})
            if quiz.id in availableQuizIds or quiz.is_free:
                quiz_data[-1]['available'] = True
            else:
                quiz_data[-1]['available'] = False
        module_price = sum([quiz['price'] for quiz in quiz_data if not quiz['available']])
        modules_data.append({'name': module.description, 'id': module.id, 'quizzes': quiz_data, 'state': 'Active', 'org_price' : module_price *2, 'price' : module_price})

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
        profile = Profile.objects.get(user = request.user)

        name = profile.user.first_name + ' ' + profile.user.last_name
        phone = profile.phone_number
        email = profile.user.email
        product = 'Tests'

        amount = sum([quiz.price for quiz in Quiz.objects.filter(id__in=[quiz for quiz in results['quizzes']])])

        order_amount = amount*100

        order_currency = 'INR'
        order_receipt = ''
        notes = {'': ''}

        # CREAING ORDER
        response = client.order.create(
            dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes, payment_capture='0'))
        order_id = response['id']
        order_status = response['status']

        for quiz in results['quizzes']:
            data = {'user': request.user.id,
                    'quiz': quiz,
                    'order_id': order_id
                    }
            available_quizzes_serializer = AvailableQuizzesSerializer(data=data)
            if available_quizzes_serializer.is_valid():
                available_quizzes_serializer.save()

        context = {}
        if order_status == 'created':
            # Server data for user convinience
            context['product_id'] = product
            context['price'] = order_amount
            context['name'] = 'missionpcs'
            context['prefill[name]'] = name
            context['prefill[contact]'] = phone
            context['prefill[email]'] = email
            context['key_id'] = key

            # data that'll be send to the razorpay for
            context['order_id'] = order_id
            context['description'] = name
            if settings.IS_DEVELOPMENT:
                context['callback_url'] = 'http://127.0.0.1:8000/letsprepare/verify_payment/'
            else:
                context['callback_url'] = 'https://missionpcs.com/letsprepare/verify_payment/'
            url = 'https://api.razorpay.com/v1/checkout/embedded'
        # paytmParams, checksum, url = get_payment_params(results['amount'], profile.phone_number, request.user.id, request.user.email, order_id)
            return JsonResponse({'paymentParams': context, 'url' : url})

    except Exception as e:
        return my_render_to_response(request, '404.html')

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
    return my_render_to_response(request, "yaksh/results.html", context={'question_papers' : question_papers_data, 'plot_div': plot_div, 'plot_div2': plot_div2,
                                                                         'course_id' : list(Course.objects.all())[0].id})


def get_accuracy_graph(question_papers_attempted, answerpapers):
    attempt_dict = {}
    qa_tups = zip(question_papers_attempted,answerpapers)
    qa_tups_ordered = [qa for qa in sorted(qa_tups, key=lambda item: item[1].end_time)]
    for qp, ap in qa_tups_ordered:
        num_attempted = len(ap.questions_answered.all())
        if qp.quiz.quiz_code in attempt_dict.keys():
            if num_attempted == 0:
                attempt_dict[qp.quiz.quiz_code].append(0)
            else:
                attempt_dict[qp.quiz.quiz_code].append(round(((ap.marks_obtained)/len(ap.questions_answered.all())*100),2))
        else:
            attempt_dict[qp.quiz.quiz_code] = []
            if num_attempted == 0:
                attempt_dict[qp.quiz.quiz_code].append(0)
            else:
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
    if len(data['error']) == 0:
        data['error'] = '_'
    try:
        error_serializer = ErrorSerializer(data=data)
        if error_serializer.is_valid():
            error_serializer.save()

        return JsonResponse({'SUCCESS': 'Thanks!!'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return JsonResponse({'error' : str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def send_otp(request):
    data = json.loads(request.POST['data'])
    number = data['number']
    otp = randint(111111,999999)
    body = 'Hi there! Your OTP to register on missionpcs is : ' + str(otp)
    try:
        send_sms(body, number)
        return JsonResponse({'SENT': otp})
    except Exception as e:
        return JsonResponse({'NUMBER NOT VALID' : str(e)})


def send_sms(body, number):
    message = tw_client.messages.create(
        body = body,
        from_= settings.twilio_number,
        to = number
    )


def index(request):
    if request.user.id == None:
        return my_render_to_response(request, "index.html")
    else:
        return my_redirect('/exam/login/?next=/letsprepare/show_modules/')

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":

        data_dict = {}
        response = request.POST
        params_dict = {
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_signature': response['razorpay_signature']
        }

        # VERIFYING SIGNATURE
        try:
            status = client.utility.verify_payment_signature(params_dict)
            data_dict['status_code'] = status
            # return data_dict
            orders = list(AvailableQuizzes.objects.filter(order_id=response['razorpay_order_id']))
            user = orders[0].user
            del data_dict['status_code']
            PaytmHistory.objects.create(user=user, **data_dict)
            for order in orders:
                order.successful = True
                order.save()
            return my_redirect('/letsprepare')
        except:
            return my_render_to_response(request, 'yaksh/404.html')
    return my_redirect('/letsprepare')