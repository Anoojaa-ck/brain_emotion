from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Users(models.Model):
    name=models.CharField(max_length=100)
    gender=models.CharField(max_length=100)
    dob=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    photo=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    place=models.CharField(max_length=100)
    USER=models.ForeignKey(User,on_delete=models.CASCADE)


class Review(models.Model):
    date = models.CharField(max_length=100)
    review = models.CharField(max_length=100)
    rating = models.CharField(max_length=100)
    USERS = models.ForeignKey(Users, on_delete=models.CASCADE)

class Brainemotion(models.Model):
    USERS = models.ForeignKey(Users, on_delete=models.CASCADE)
    date = models.DateField()
    result = models.CharField(max_length=100)
    upload = models.CharField(max_length=250)


class Diary(models.Model):
    date = models.DateField()
    time = models.TimeField()
    emotion = models.CharField(max_length=200)
    text_emotion = models.CharField(max_length=200)
    content = models.CharField(max_length=1000)
    USERS = models.ForeignKey(Users, on_delete=models.CASCADE)

class heartbeat(models.Model):
    date = models.DateField()
    time = models.TimeField()
    count= models.CharField(max_length=200)
    USERS = models.ForeignKey(Users, on_delete=models.CASCADE)



