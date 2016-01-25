from django.db import models
from django.utils import timezone
from django.db.models import Max
from django.utils.html import escape

# User class for built-in authentication module
from django.contrib.auth.models import User

class Credit(models.Model):
	hoursLearned = models.IntegerField(null=True)
	hoursTaught = models.IntegerField(null=True)

class Guru(models.Model):
	user = models.OneToOneField(User)
	location = models.CharField(max_length=50)
	rating = models.FloatField(null=True)
	level = models.CharField(max_length=50)
	followers = models.ManyToManyField("self", related_name="followers")
	following = models.ManyToManyField("self", related_name="following")
	picture = models.ImageField(blank=True, upload_to="guru-photos", default="/media/guru-photos/person.jpg")
	skills = models.CharField(max_length=500) 
	bio = models.CharField(max_length=400)
	age = models.IntegerField(null=True)
	credit = models.OneToOneField(Credit)
	interested = models.ManyToManyField('Listing', related_name = 'interested', default=None)
	needsConfirmation = models.ManyToManyField('Listing', related_name = 'needsConfirmation', default=None)
	rejected = models.ManyToManyField('Listing', related_name = 'rejected', default=None)
	confirmed = models.ManyToManyField('Listing', related_name = 'confirmed', default=None)
	reviewsReceived = models.IntegerField(default=0)


class Listing(models.Model): 
	subject = models.CharField(max_length=42)
	location = models.CharField(max_length=50, default="N/A")
	description = models.CharField(max_length=500)
	guru = models.ForeignKey(Guru)
	date = models.DateTimeField(default=timezone.now)
	skillType = models.CharField(max_length=40)
	#session = models.ForeignKey('MySession', default=None, null=True) # a session has many listings
	#session = models.ManyToManyField('MySession', default=None, null=True)

class DateAndTime(models.Model):
	date = models.CharField(max_length=20)
	fromTime = models.CharField(max_length=5) # 24 hr time?
	toTime = models.CharField(max_length=5)
	instructorTimes = models.ManyToManyField('MySession', related_name = 'instructorTimes', default=None)
	studentTimes = models.ManyToManyField('MySession', related_name = 'studentTimes', default=None)

class MySession(models.Model):
	#listing = models.ManyToManyField('Listing', related_name='listing', default=None)
	student = models.ManyToManyField('Guru', related_name='student', default=None)
	listing = models.OneToOneField(Listing, related_name='listing')
	#student = models.OneToOneField(Guru, related_name = 'student')
	#listing = models.ForeignKey(Listing)
	#student = models.ForeignKey(Guru)
	status = models.CharField(max_length=20, default="N/A") # pending, confirmed, rejected
	proposedTime = models.CharField(max_length=30, default="N/A")
	progress = models.CharField(max_length=20, default="N/A") # in progress, completed, upcoming
	reviewed = models.BooleanField(default=False)

class Review(models.Model): 
	session = models.OneToOneField(MySession, related_name = 'session')
	#guru = models.OneToOneField(Guru, related_name = 'reviewer')
	#reviewedUser = models.OneToOneField(Guru, related_name = 'reviewee')
	rating = models.FloatField(null=True)
	date = models.DateTimeField(default=timezone.now)
	description = models.CharField(max_length=500)

class Message(models.Model):
	fromGuru = models.ForeignKey(Guru, related_name = 'fromGuru')
	toGuru = models.ForeignKey(Guru, related_name = 'toGuru')
	date = models.DateTimeField(default=timezone.now)
	subject = models.CharField(max_length=100)
	body = models.TextField(null=True)
	numReplies = models.IntegerField(default=1)

class Reply(models.Model):
	fromGuru = models.ForeignKey(Guru, related_name = 'fromReply')
	toGuru = models.ForeignKey(Guru, related_name = 'toReply')
	message = models.ForeignKey(Message)
	date = models.DateTimeField(default=timezone.now)
	body = models.TextField(null=True)

class Person(models.Model):
	usernames = models.CharField(max_length=20)
	skills = models.CharField(max_length=500) 
	timestamp = models.DateTimeField(default=timezone.now)

class Interest(models.Model):
	username = models.CharField(max_length=20)
	interestList = models.CharField(max_length=2000)