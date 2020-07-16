from django.db import models

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
    order_id = models.CharField(max_length=255, default='TRIAL')
    successful = models.BooleanField(null=False ,default=False)

class PaytmHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    MID = models.CharField(max_length=40)
    TXNID = models.CharField('TXNID', max_length=100)
    ORDERID = models.CharField('ORDER ID', max_length=100)
    BANKTXNID = models.CharField('BANK TXN ID', null=True, blank=True, max_length=100)
    TXNAMOUNT = models.CharField('TXN AMOUNT', max_length=100)
    CURRENCY = models.CharField('CURRENCY', max_length=4, null=True, blank=True)
    STATUS = models.CharField('STATUS', max_length=12)
    RESPCODE = models.CharField('RESP CODE', max_length=100)
    RESPMSG = models.CharField('RESP MSG', max_length=250)
    TXNDATE = models.CharField('TXN DATE', default='NOW', max_length=100)
    GATEWAYNAME = models.CharField("GATEWAY NAME", max_length=100, null=True, blank=True)
    BANKNAME = models.CharField('BANK NAME', max_length=50, null=True, blank=True)
    PAYMENTMODE = models.CharField('PAYMENT MODE', max_length=10, null=True, blank=True)
