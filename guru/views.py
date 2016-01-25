#import autocomplete_light.shortcuts as al
#al.autodiscover()
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from guru.forms import *
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.core import serializers
from django.http import HttpResponse
from itertools import chain
from django.db.models import Q
import json
from django.core import serializers
from datetime import datetime
from ipware.ip import get_ip
import requests
import math
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import TwilioRestClient
import random
import string
from django.core.mail import send_mail

allInterests = ["Android Development","iOS Development","Web Application Development",
"Hardware","Software","Electronic Media","Print","Animation","Recipes","Techniques",
"Brand","Fashion","Product","Decorative","Drawing","Glass","Painting","Electrical",
"Interior Design","Landscape","Decorations","Plumbing","Biology","Chemistry",
"Physics","Non-Fiction","Fiction","Physical","Mental","Economics","Entrepeneurship",
"Black and White Photography","Color Photography","Auditing","Taxes","Documents","Images","Body Building",
"Weight Loss","Personal Trainer","Employment counsellor","Resume","Speaking","Writing"
]


@login_required
def home(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture

	student_sessions = MySession.objects.filter(student=guru)

	teacher_sessions = MySession.objects.filter(listing__guru=guru)

	context['student_sessions'] = student_sessions
	context['teacher_sessions'] = teacher_sessions
	
	context['creditAccumulated'] = Credit.objects.get(guru=guru).hoursTaught
	context['creditSpent'] = Credit.objects.get(guru=guru).hoursLearned
	context['creditRemaining'] = context['creditAccumulated'] - context['creditSpent']

	for s in student_sessions:

		if s.proposedTime != 'N/A':
			arr = s.proposedTime.split(" ")
			time1 = arr[0] + " " + arr[1]
			time2 = arr[0] + " " + arr[3]
			# 11/02/2015 9:00 to 10:00
			date_obj1 = datetime.strptime(time1, '%m/%d/%Y %H:%M')
			date_obj2 = datetime.strptime(time2, '%m/%d/%Y %H:%M')
			now = datetime.now() 
			#.strftime('%m/%d/%Y %H:%M')

			if now > date_obj2:
				s.progress = "completed"
			elif now < date_obj1:
				s.progress = "upcoming"
			elif now >= date_obj1 and now <= date_obj2:
				s.progress = "in progress"
			else:
				s.progress = "N/A"

			s.save()

	for i in teacher_sessions:

		if i.proposedTime != 'N/A':
			arr = i.proposedTime.split(" ")
			time1 = arr[0] + " " + arr[1]
			time2 = arr[0] + " " + arr[3]
			# 11/02/2015 9:00 to 10:00
			date_obj1 = datetime.strptime(time1, '%m/%d/%Y %H:%M')
			date_obj2 = datetime.strptime(time2, '%m/%d/%Y %H:%M')
			now = datetime.now() 
			#.strftime('%m/%d/%Y %H:%M')

			if now > date_obj2:
				i.progress = "completed"
			elif now < date_obj1:
				i.progress = "upcoming"
			elif now >= date_obj1 and now <= date_obj2:
				i.progress = "in progress"
			else:
				i.progress = "N/A"

			i.save()


	ip = get_ip(request)
	if ip is not None:
		#This part is taken from ipinfo.io usage documentation
		ipLoc = requests.get('http://ipinfo.io/%s/json' % ip)
		data = ipLoc.json()
		
		if 'region' in data and 'city' in data:	
			print(data)
			reg = data['region'] #error checking for both city and 
			city = data['city'] #the state
			g = Guru.objects.get(user=request.user)
			g.location = str(city + "," + reg)
			g.save()

	matches = Listing.objects.filter(skillType="None");

	toDisplay = json.loads(Interest.objects.get(
		username=request.user.username).interestList)
	for x in xrange(len(toDisplay)):
		matches = matches | Listing.objects.filter(skillType=toDisplay[x])
	context['allListings'] = matches

	# if a session is "completed" and not reviewed, prompt user to review
	# after 24 hours if user does not leave review, credit transfers anyway
 
	notReviewed = MySession.objects.filter(student=guru, progress="completed", reviewed=False)
	
	
	context['needsReview'] = notReviewed
	context['numNotReviewed'] = len(notReviewed)

	return render(request, 'guru/home.html', context)

def register(request, create_registration_form=RegistrationForm()):
	context = {"create_registration_form" :  create_registration_form}
	return render(request, 'guru/register.html', context)

@login_required
def inbox(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
	messages = Message.objects.filter(toGuru=guru).order_by('-date')
	sentMessages = Message.objects.filter(fromGuru=guru).filter(Q(numReplies__gt=1)).order_by('-date')
	result = sorted(chain(messages,sentMessages),key=lambda instance: instance.date, reverse=True)
	replies = []
	reply = {'body':'body', 'date':'date'}
	for sentMessage in sentMessages:
		if len(sentMessage.reply_set.all()) > 0:
			# if there's a reply then populate in inbox
			latest = sentMessage.reply_set.all().order_by('-date')[0]
			reply['body'] = latest.body
			
			reply['date'] = latest.date
			replies += reply

	context['messages'] = result
	context['replies'] = replies
	return render(request, 'guru/inbox.html', context)

@login_required
def compose(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
	context['msgusername'] = ''
	return render(request, 'guru/compose.html', context)

@login_required
def lcompose(request,id):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
	context['msgusername'] = User.objects.get(id=id).username
	return render(request, 'guru/compose.html', context)


@login_required
def interested(request, id):
	context = {}
	context['currUser'] = request.user
	# add request guru to listing interested gurus field
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
	listing = Listing.objects.get(id=id)
	listing.interested.add(guru)
	listing.needsConfirmation.add(guru)
	listing.save()

	return redirect(reverse('postdetails', kwargs={'id':id}))

@login_required
def uninterested(request, id):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
	listing = Listing.objects.get(id=id)

	if guru in listing.interested.all():
		listing.interested.remove(guru)
		listing.needsConfirmation.remove(guru)
		listing.save()

	return redirect(reverse('postdetails', kwargs={'id':id}))

@login_required
def activity(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture

	# get all of logged in user's interested listings
	pending = Listing.objects.filter(interested=guru).order_by('-date')

	rejections = Listing.objects.filter(rejected=guru).order_by('-date')
	confirmed = Listing.objects.filter(confirmed=guru).order_by('-date')

	needsConfirmation = Guru.objects.filter(needsConfirmation__guru=guru)

	myListings = Listing.objects.filter(guru=guru).order_by('-date') #.exclude(mysession__listing__progress="completed")
 
	upcomingData = dict()
	completedData = dict()
 
	for l in myListings:
		s = MySession.objects.get(listing=l)
		if s.id not in upcomingData and s.progress != "completed":
			upcomingData[s.id] = s
		if s.id not in completedData and s.progress == "completed":
			completedData[s.id] = s
	context['upcomingData'] = upcomingData
	context['completedData'] = completedData


	d = dict()
	requests = {}

	for user in needsConfirmation:
		if user.user.username not in d:
			d[user.user.username] = 1
		else:
			d[user.user.username] += 1

	for key in d:
		user = Guru.objects.filter(user__username=key)
		a = Listing.objects.filter(interested=user)
	
		requests[user] = a


	context['pending'] = pending
	context['rejections'] = rejections
	context['confirmed'] = confirmed
	context['requests'] = requests
	return render(request, 'guru/activity.html', context)

@login_required
def dismissRequest(request, reqInfo):

	info = reqInfo.split('_')
	
	subject = info[0]
	username = info[1]
	guru = Guru.objects.get(user__username=username)
	listing = Listing.objects.get(subject=subject) # change to listing ID later instead of subj

	if guru in listing.interested.all():
		listing.interested.remove(guru)
		listing.needsConfirmation.remove(guru)
		listing.rejected.add(guru)
		listing.save()

	return HttpResponse("")

@login_required
def dismiss_sched(request):
	errors = {}
	incomplete = False
	if not 'sessionId' in request.POST or not request.POST['sessionId']:	
		errors['sessionId'] = False
		incomplete = True

	if incomplete:
		raise Http404
	else:
		session = MySession.objects.get(id=request.POST['sessionId'])
		session.status = 'rejected'
		session.save()

		return HttpResponse("")

@login_required
def confirm_sched(request):
	errors = {}
	incomplete = False
	if not 'sessionId' in request.POST or not request.POST['sessionId']:	
		errors['sessionId'] = False
		incomplete = True

	if incomplete:
		raise Http404
	else:
		session = MySession.objects.get(id=request.POST['sessionId'])
		session.status = 'confirmed'
		session.save()
		return HttpResponse("")

@login_required
def confirmRequest(request):
	
	errors = {}
	incomplete = False
	if not 'user' in request.POST or not request.POST['user']:
		errors['user'] = False
		incomplete = True
	if not 'listingTitle' in request.POST or not request.POST['listingTitle']:
		errors['listingTitle'] = False
		incomplete = True

	if incomplete:
		raise Http404
	else:
		guru = Guru.objects.get(user__username=request.POST['user'])
		listing = Listing.objects.get(subject=request.POST['listingTitle']) # change to listing ID later instead of subj

		if guru in listing.interested.all():
			listing.interested.remove(guru)
			listing.needsConfirmation.remove(guru)
			listing.confirmed.add(guru)

			listing.save()
			# create a session
			session = MySession.objects.get(listing=listing)
			session.student.add(guru)
			session.save()
		return HttpResponse("")

@login_required
def schedule(request, listingId, guruId):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture

	listing = Listing.objects.get(id=listingId)
	lguru = Guru.objects.get(id=guruId)
	context['listing'] = listing
	context['lguru'] = lguru
	context['studentOrInstructor'] = 'instructor'

	session = MySession.objects.get(listing__id=listingId, 
									student__id=guruId)

	i_dts = session.instructorTimes.all()
	s_dts = session.studentTimes.all()
	context['i_dts'] = i_dts
	context['s_dts'] = s_dts
	context['status'] = session.status
	context['proposedTime'] = session.proposedTime
	context['sessionId'] = session.id

	return render(request, 'guru/schedule.html', context)

@login_required
def studentSchedule(request, listingId):
	context =  {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
	context['studentOrInstructor'] = 'student'

	listing = Listing.objects.get(id=listingId)
	lguru = Guru.objects.get(user=request.user)
	context['listing'] = listing
	context['lguru'] = lguru

	session = MySession.objects.get(listing__id=listingId, 
									student__id=lguru.id)

	i_dts = session.instructorTimes.all()
	s_dts = session.studentTimes.all()
	context['i_dts'] = i_dts
	context['s_dts'] = s_dts
	context['status'] = session.status
	context['sessionId'] = session.id
	context['proposedTime'] = session.proposedTime

	return render(request, 'guru/schedule.html', context)

@login_required
def confirm_date(request):
	temp = {}
	incomplete = False

	if not 'cdate' in request.POST or not request.POST['cdate']:	
		incomplete = True
		temp['cdate'] = False
	if not 'listingID' in request.POST or not request.POST['listingID']:
		incomplete = True
		temp['listingID'] = False
	if not 'studentID' in request.POST or not request.POST['studentID']:
		incomplete = True
		temp['studentID'] = False
	if not 'studentOrInstructor' in request.POST or not request.POST['studentOrInstructor']:
		incomplete = True
		temp['studentOrInstructor'] = False

	if incomplete:
		raise Http404
	else:

		session = MySession.objects.get(listing__id=request.POST['listingID'], 
										student__id=request.POST['studentID'])

		session.proposedTime = request.POST['cdate']
		session.status = "pending"
		session.save()


		if request.POST['studentOrInstructor'] == 'instructor':
			return redirect(reverse('schedule', 
					kwargs={'listingId':request.POST['listingID'], 'guruId':request.POST['studentID']}))
		else:
			return redirect(reverse('studentSchedule',
					kwargs={'listingId':request.POST['listingID']}))

@login_required
def add_date(request):
	context = {}
	temp = {}
	incomplete = False
	if not 'date' in request.POST or not request.POST['date']:
		incomplete = True
		temp['date'] = False
	if not 'fromTime' in request.POST or not request.POST['fromTime']:
		incomplete = True
		temp['fromTime'] = False
	if not 'toTime' in request.POST or not request.POST['toTime']:
		incomplete = True
		temp['toTime'] = False
	if not 'fromAMPM' in request.POST or not request.POST['fromAMPM']:
		incomplete = True
		temp['fromAMPM'] = False
	if not 'toAMPM' in request.POST or not request.POST['toAMPM']:
		incomplete = True
		temp['toAMPM'] = False
	if not 'listingID' in request.POST or not request.POST['listingID']:
		incomplete = True
		temp['listingID'] = False
	if not 'studentID' in request.POST or not request.POST['studentID']:
		incomplete = True
		temp['studentID'] = False
	if not 'studentOrInstructor' in request.POST or not request.POST['studentOrInstructor']:
		incomplete = True
		temp['studentOrInstructor'] = False

	if incomplete:
		raise Http404
	else:
		fromTime = request.POST['fromTime'] +  " " + request.POST['fromAMPM']
		toTime = request.POST['toTime'] + " " + request.POST['toAMPM']
 
		# convert to 24 time
		cf = datetime.strptime(fromTime, '%I:%M %p')
		ct = datetime.strptime(toTime, '%I:%M %p')
 
		c_fromTime = cf.strftime("%H:%M")
		c_toTime = ct.strftime("%H:%M")
 
		dt = DateAndTime(date=request.POST['date'], 
						fromTime=c_fromTime, 
						toTime=c_toTime)
		dt.save()

		#query session using listing id
		session = MySession.objects.get(listing__id=request.POST['listingID'], 
										student__id=request.POST['studentID'])

		# students and instructors add dates separately but can see each others dates
		print(request.POST['studentOrInstructor'])
		if request.POST['studentOrInstructor'] == 'student':
			context['studentOrInstructor'] = 'student'
			session.studentTimes.add(dt)
			session.save()
		elif request.POST['studentOrInstructor'] == 'instructor':
			context['studentOrInstructor'] = 'instructor'
			session.instructorTimes.add(dt)
			session.save()

		i_dts = session.instructorTimes.all()
		s_dts = session.studentTimes.all()

		context['i_dts'] = i_dts
		context['s_dts'] = s_dts

	if request.POST['studentOrInstructor'] == 'instructor':
		return redirect(reverse('schedule', 
				kwargs={'listingId':request.POST['listingID'], 'guruId':request.POST['studentID']}))
	else:
		return redirect(reverse('studentSchedule',
				kwargs={'listingId':request.POST['listingID']}))


@login_required
def delete_date(request, id):
	# currently fked up need to fix bug

	context = {}
	errors = []
	try:
		item_to_delete = DateAndTime.objects.get(id=id)
		item_to_delete.delete()
	except ObjectDoesNotExist:
		errors.append('The date did not exist in the dates list.')

	dts = DateAndTime.objects.all()
	context['items'] = dts
	context['errors'] = errors

	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
	return render(request, 'guru/schedule.html', context)

@login_required
def get_dates(request):
	me = Guru.objects.get(user=request.user)
	isessions = MySession.objects.filter(listing__guru=me)
	ssessions = MySession.objects.filter(student=me)

	# create json that separates instructor times from student times
	idata = []
	sdata = []
	data = {}
	
	for session in isessions:
		sesh = {}
		sesh['listingId'] = session.listing.id	
		it = session.instructorTimes.all()
		st = session.studentTimes.all()
		arr = []
		arr2 = []
		for i in it:
			temp = {}
			temp['id'] = i.id
			temp['fromTime'] = i.fromTime
			temp['toTime'] = i.toTime
			temp['date'] = i.date
			arr.append(temp) # [ {id, fromtime, totime, date } { ... } ]
		sesh['its'] = arr
		for i in st:
			temp = {}
			temp['id'] = i.id
			temp['fromTime'] = i.fromTime
			temp['toTime'] = i.toTime
			temp['date'] = i.date
			arr2.append(temp) # [ {id, fr
		sesh['sts'] = arr2
		idata.append(sesh)
	for session in ssessions:
		sesh = {}
		sesh['listingId'] = session.listing.id
		it = session.instructorTimes.all()
		st = session.studentTimes.all()
		arr = []
		arr2 = []
		for i in it:
			temp = {}
			temp['id'] = i.id
			temp['fromTime'] = i.fromTime
			temp['toTime'] = i.toTime
			temp['date'] = i.date
			arr.append(temp) # [ {id, fromtime, totime, date } { ... } ]
		sesh['its'] = arr
		for i in st:
			temp = {}
			temp['id'] = i.id
			temp['fromTime'] = i.fromTime
			temp['toTime'] = i.toTime
			temp['date'] = i.date
			arr2.append(temp) 
		sesh['sts'] = arr2
		sdata.append(sesh)
	data['idata'] = idata
	data['sdata'] = sdata
	return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def getusernames(request):
	users = User.objects.all()
	temp = '['
	for user in users:
		temp += '{"name": '
		temp += '"'
		temp += user.username
		temp += '"}'
		temp += ','
	
	temp = temp[0:len(temp)-1]
	temp += ']'
	return HttpResponse(temp, content_type="application/json")

@login_required
def getcategories(request):
	temp = '['
	for x in xrange(len(allInterests)):
		temp += '{"name": '
		temp += '"'
		temp += allInterests[x]
		temp += '"}'
		temp += ','
	
	temp = temp[0:len(temp)-1]
	temp += ']'
	return HttpResponse(temp, content_type="application/json")


@login_required
def sendreply(request):
	context = {}
	if request.method == 'GET':
		return render(request, 'guru/inbox.html', context)

	errors = []
	context['errors'] = errors

	if not 'replytext' in request.POST or not request.POST['replytext']:
		errors.append('Reply Text is required.')
	else:
		context['replytext'] = request.POST['replytext']

	if not 'messageId' in request.POST or not request.POST['messageId']:
		errors.append('Message ID is required.')
	else:
		context['messageId'] = request.POST['messageId']

	guru = Guru.objects.get(user=request.user)
	message = Message.objects.get(id=context['messageId'])

	if message.fromGuru.user.username == guru.user.username:
		toGuru = message.toGuru
	elif message.toGuru.user.username == guru.user.username:
		toGuru = message.fromGuru

	# update the message subj line
	message.numReplies = message.numReplies + 1
	message.subject = "("+str(message.numReplies)+") "+context['replytext']
	message.save()

	fromGuru = guru 
	body = context['replytext']

	reply = Reply(fromGuru=fromGuru, 
				toGuru=toGuru,
				message=message,
				body=body)

	reply.save()

	context['message'] = message
	context['currUser'] = request.user
	context['image'] = guru.picture

	#return render(request, 'guru/inbox.html', context)
	return redirect(reverse('inbox'))

@login_required
def sendmessage(request):
	context = {}
	if request.method == 'GET':
		return render(request, 'guru/inbox.html', context)

	errors = []
	context['errors'] = errors

	if not 'to' in request.POST or not request.POST['to']:
		errors.append('Recipient username is required.')
	else:
		context['to'] = request.POST['to']

	if not 'subject' in request.POST or not request.POST['subject']:
		errors.append('Subject line is required.')
	else:
		context['subject'] = request.POST['subject']

	if not 'description' in request.POST or not request.POST['description']:
		errors.append('Description is required.')
	else:
		context['description'] = request.POST['description']

	guru = Guru.objects.get(user=request.user)
	context['currUser'] = request.user
	context['image'] = guru.picture

	# send the Message to one or multiple users
	to = context['to']
	recipients = to.split(',')

	for recipient in recipients:
		guru_recip = Guru.objects.get(user__username=recipient)
		new_msg = Message(fromGuru=guru,
							toGuru=guru_recip,
							subject=request.POST['subject'], 
							body=request.POST['description'])
		new_msg.save()

	#return render(request, 'guru/inbox.html', context)
	return redirect(reverse('inbox'))

@login_required
def messageExpanded(request, id):
	context = {}
	guru = Guru.objects.get(user=request.user)
	context['currUser'] = request.user
	context['image'] = guru.picture
	message = Message.objects.get(id=id)
	context['message'] = message
	context['fromGuru'] = message.fromGuru
	return render(request, 'guru/messageexpanded.html', context)

@login_required
def reminders(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture




	return render(request, 'guru/reminders.html', context)

@login_required
def sendtext(request):
	print("wtf")
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture

	if request.method == 'GET':
		print("Fghfg")
		return redirect(reverse('reminders'))
	else:

		print("Wtf")
		errors = []
		context['errors'] = errors
		print(request.POST)

		if not 'cellnum' in request.POST or not request.POST['cellnum']:
			errors.append('Cell number is required.')
		else:
			context['cellnum'] = request.POST['cellnum']

		if not 'message' in request.POST or not request.POST['message']:
			errors.append('Message is required.')
		else:
			context['message'] = request.POST['message']

		print(request.POST['cellnum'])
		print(request.POST['message'])
		

	# Your Account Sid and Auth Token from twilio.com/user/account
		account_sid =  "AC9527506d18397f7e41e04c284d783961" #"{{ account_sid }}"
		auth_token  = "f578ff85cad7c621bbd741f7c3223762" #"{{ auth_token }}"
		client = TwilioRestClient(account_sid, auth_token)

		if len(errors) == 0:
			message = client.messages.create(
			    body=request.POST['message'],
			    to=request.POST['cellnum'],
			    from_="+17327985311")
			print message.sid

		return render(request, 'guru/reminders.html', context)

@login_required
def calendar(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
	return render(request, 'guru/calendar.html', context)
@login_required
def myreviews(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture

	notReviewed = MySession.objects.filter(student=guru, progress="completed", reviewed=False)
	context['needsReview'] = notReviewed
	context['numNotReviewed'] = len(notReviewed)

	myReviews = Review.objects.filter(session__student=guru).order_by('-date')
	context['myReviews'] = myReviews
	return render(request, 'guru/myreviews.html', context)

@login_required
def postReview(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
 
	if request.method == 'GET':
		return redirect(reverse('myreviews'))
	errors = []
	context['errors'] = errors
 
	if not 'rating' in request.POST or not request.POST['rating']:
		errors.append('Rating is required')
	else:
		context['rating'] = request.POST['rating']
 
	if not 'feedback' in request.POST or not request.POST['feedback']:
		errors.append('Feedback is required.')
	else:
		context['feedback'] = request.POST['feedback']
 
	if not 'sessionId' in request.POST or not request.POST['sessionId']:
		errors.append('Session ID is required.')
	else:
		context['sessionId'] = request.POST['sessionId']
 
	#create a new review
	session = MySession.objects.get(id=request.POST['sessionId'])
 
	review = Review(session=session,
					rating=request.POST['rating'],
					description=request.POST['feedback'])
	review.save()
 
	# get the reviewed user's rating, and update it
 
	instructor = session.listing.guru
	currAvg = instructor.rating
 
 
	if currAvg == 0:
		instructor.rating = request.POST['rating']
		instructor.reviewsReceived = instructor.reviewsReceived + 1
		instructor.save()
	else:
		instructor.reviewsReceived = instructor.reviewsReceived + 1
		newAvg = currAvg + (int(request.POST['rating']) - currAvg)/(instructor.reviewsReceived)
		instructor.rating = math.ceil(newAvg)
		instructor.save()
 
	session.reviewed = True
	session.save()
 
 
	# then transfer credit 
 
	time = session.proposedTime
 
	arr = time.split(" ")
	time1 = arr[1]
	time2 = arr[3]
 
	fmt = "%H:%M"
	tdelta = datetime.strptime(time2, fmt) - datetime.strptime(time1, fmt)
	roundedCredit = int(math.ceil(tdelta.seconds/3600.0))
 
	# transfer from guru -> instructor
	myCredit = Credit.objects.get(guru=guru)
	instructorCredit = Credit.objects.get(guru=instructor)
 
	instructorCredit.hoursTaught = instructorCredit.hoursTaught+roundedCredit
	myCredit.hoursLearned = myCredit.hoursLearned+roundedCredit
	
	instructorCredit.save()
	myCredit.save()
 
   # TODO: make sure user has enough credit before making a transaction
   # negative credit 
	return redirect(reverse('myreviews'))
 
 
@login_required
def reviewSession(request, sessionId):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
 
	session = MySession.objects.get(id=sessionId)
 
	context['session'] = session
	return render(request, 'guru/review.html', context)

@login_required
def settings(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
	return render(request, 'guru/settings.html', context)

@login_required
def searchresults(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
	return render(request, 'guru/searchresults.html', context)

@login_required
def postdetails(request, id):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture

	listing = Listing.objects.get(id=id)
	context['listing'] = listing

	context['interested'] = False
	allInterested = listing.interested.all()
	if guru in allInterested:
		context['interested'] = True
	return render(request, 'guru/postdetails.html', context)

@login_required
def pprofile(request, username):
	guru = Guru.objects.get(user__username=username)
	userId = guru.user.id
	return redirect(reverse('profile', kwargs={'id':userId}))

@login_required
def profile(request, id):
	context = {}
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
	context['currUser'] = request.user
	#return render(request, 'guru/profile.html', context)
	try:    
		user = User.objects.get(pk=id)
	except User.DoesNotExist:
		user = None

	if user is None:
		return redirect(reverse('home'))
	else:
		lookupGuru = Guru.objects.get(user = user)
		me = Guru.objects.get(user = request.user)
		context['me'] = me
		context['lookupGuru'] = lookupGuru
		rating = lookupGuru.rating

		fraction = 0
		if (rating % 1 == 0.5):
			fraction = 1

		wholes = int(rating)
		emptys = 5 - fraction - wholes

		context['lookupImage'] = lookupGuru.picture
		context['wholes'] = range(0,wholes)
		context['fraction'] = range(0,fraction)
		context['emptys'] = range(0,emptys)

		 # get all the reviews made for this user
		reviews = Review.objects.filter(session__listing__guru=lookupGuru).order_by('-date')
		context['reviews'] = reviews
		
		return render(request, 'guru/profile.html', context)
@login_required
def editprofile(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture

	entry_to_edit = get_object_or_404(Guru, user=request.user)

	if request.method == 'GET':
		form = EditProfileForm(instance=entry_to_edit)  
		context['form'] = form
		context['profile'] = entry_to_edit         
		return render(request, 'guru/editprofile.html', context)


	# if method is POST, get form data to update the model
	form = EditProfileForm(request.POST, request.FILES, instance=entry_to_edit)
	

	if not form.is_valid():
		context['form'] = form
		context['profile'] = entry_to_edit   
		return render(request, 'guru/editprofile.html', context)
	   
	# if profile doesn't exist, create a new one
	profile = Guru.objects.get(user = request.user)

	if (profile is None):
		profile = Guru(user=request.user, 
					   location = form.cleaned_data['location'],
					   skills = form.cleaned_data['skills'], 
					   rating = profile.rating,
					   level = profile.level,
					   age = form.cleaned_data['age'],
					   bio = form.cleaned_data['bio'],
					   picture = form.cleaned_data['picture'],
					   credit = profile.credit)
		profile.save()
	# else alter the existing model with the edited fields
	else:
		profile.location = form.cleaned_data['location']
		profile.skills = form.cleaned_data['skills']
		profile.age = form.cleaned_data['age']
		profile.bio = form.cleaned_data['bio']
		profile.picture = form.cleaned_data['picture']
		profile.save()
	
	return render(request, 'guru/editprofile.html', context)

@login_required
def addlisting(request):
	context = {}
	if request.method == 'GET':
		return render(request, 'guru/alllistings.html', context)

	errors = []
	context['errors'] = errors
	if not 'skillType' in request.POST or not request.POST['skillType']:
		errors.append('Skill Tag is required')
	else:
		context['skillType'] = request.POST['skillType']

	if not 'title' in request.POST or not request.POST['title']:
		errors.append('Title is required.')
	else:
		context['title'] = request.POST['title']

	if not 'location' in request.POST or not request.POST['location']:
		errors.append('Location is required.')
	else:
		context['location'] = request.POST['location']

	if not 'description' in request.POST or not request.POST['description']:
		errors.append('Description is required.')
	else:
		context['description'] = request.POST['description']

	guru = Guru.objects.get(user=request.user)
	context['currUser'] = request.user
	context['image'] = guru.picture

	if errors != [] :
		context['errors'] = errors
		return render(request, 'guru/newlisting.html',context)
	

	new_listing = Listing(subject=request.POST['title'], location=request.POST['location'], 
							description=request.POST['description'], 
							guru=guru,skillType=request.POST['skillType'])
	new_listing.save()

	 #create a session too 
	new_session = MySession(listing=new_listing)
	new_session.save()
 
	matches = Listing.objects.filter(skillType="None")

	toDisplay = json.loads(Interest.objects.get(
		username=request.user.username).interestList)
	for x in xrange(len(toDisplay)):
		matches = matches | Listing.objects.filter(skillType=toDisplay[x])
	context['allListings'] = matches

	return redirect(reverse('allListings'))


@login_required
def newListing(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture
	context['location'] = guru.location
	return render(request, 'guru/newlisting.html', context)

@login_required
def allListings(request):
	context = {}
	context['currUser'] = request.user
	guru = Guru.objects.get(user=request.user)
	context['image'] = guru.picture

	context['allListings'] = Listing.objects.all().order_by('-date')
	return render(request, 'guru/alllistings.html', context)

def createNewUser(request):
	form = RegistrationForm(request.POST)
	if not form.is_valid():
		return register(request, create_registration_form=form)

	username = form.cleaned_data['username']
	password = form.cleaned_data['password']
	email = form.cleaned_data['email']
	firstname = form.cleaned_data['firstname']
	lastname = form.cleaned_data['lastname']
	
	new_user = User.objects.create_user(username=username, 
		email=email, password=password,first_name=firstname,last_name=lastname)
	new_user.save()

	credit = Credit(hoursLearned=0,
					hoursTaught=0)
	credit.save()

	new_person = Person(usernames=username,skills="N/A")
	new_person.save()
	# create a Guru model containing the user's profile that you can edit later
	new_profile = Guru(user=new_user, # default fields when you first register
					   location="N/A",
					   rating=0,
					   level="noob",
					   skills="N/A",
					   bio="N/A",
					   age=0,
					   credit=credit)


	new_profile.save()

	new_user = authenticate(username=form.cleaned_data['username'], \
		password=form.cleaned_data['password'])
	login(request, new_user)

	context = {}
	context['currUser'] = request.user

	return redirect(reverse('addInterests'))


def reset(request, create_reset_form=ResetForm()):
	context = {"create_reset_form" : create_reset_form}
	return render(request, 'guru/passwordreset.html', context)


def resetpassword(request, create_reset_form=ResetForm()):
	form = ResetForm(request.POST)
	context = {"create_reset_form" : create_reset_form}
	if not form.is_valid():
		context['errors'] = form.errors
		return render(request, 'guru/passwordreset.html', context)
	cleanedEmail = form.cleaned_data['email']
	userold = User.objects.get(email=cleanedEmail)
	toResetPass = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
	userold.set_password(toResetPass)
	userold.save()

	resetMessage = "Hello! You have requested an password reset for your timeShare account \
	the password has been reset to " + toResetPass + " please use this temporary \
	password to reset access your account"
	send_mail(subject='Your Password Reset', message=resetMessage, from_email='cmuwebapps437@gmail.com',
    recipient_list=[cleanedEmail])

	return redirect(reverse('home'))

@login_required
def addInterests(request):
	context = [];
	return render(request,'guru/Interest.html', context)

@login_required
def saveInterests(request):
	CheckBoxes = []
	if(Interest.objects.filter(username=request.user.username)):
		Interest.objects.get(username=request.user.username).delete();
	cb1 = request.POST.getlist("Android Development")
	if('on' in cb1):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb2 = request.POST.getlist("iOS Development")
	if('on' in cb2):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)

	cb3 = request.POST.getlist("Web Application Development")
	if('on' in cb3):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb4 = request.POST.getlist("Hardware")
	if('on' in cb4):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb5 = request.POST.getlist("Software")
	if('on' in cb5):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb6 = request.POST.getlist("Electronic Media")
	if('on' in cb6):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb7 = request.POST.getlist("Print")
	if('on' in cb7):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb8 = request.POST.getlist("Animation")
	if('on' in cb8):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb9 = request.POST.getlist("Recipes")
	if('on' in cb9):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb10 = request.POST.getlist("Techniques")
	if('on' in cb10):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb11 = request.POST.getlist("Brand")
	if('on' in cb11):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb12 = request.POST.getlist("Fashion")
	if('on' in cb12):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb13 = request.POST.getlist("Product")
	if('on' in cb13):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb14 = request.POST.getlist("Decorative")
	if('on' in cb14):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb15 = request.POST.getlist("Drawing")
	if('on' in cb15):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb16 = request.POST.getlist("Glass")
	if('on' in cb16):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb17 = request.POST.getlist("Painting")
	if('on' in cb17):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb18 = request.POST.getlist("Electrical")
	if('on' in cb18):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb19 = request.POST.getlist("Interior Design")
	if('on' in cb19):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb20 = request.POST.getlist("Landscape")
	if('on' in cb20):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb21 = request.POST.getlist("Decorations")
	if('on' in cb21):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb22 = request.POST.getlist("Plumbing")
	if('on' in cb22):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb23 = request.POST.getlist("Biology")
	if('on' in cb23):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb24 = request.POST.getlist("Chemistry")
	if('on' in cb24):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb25 = request.POST.getlist("Physics")
	if('on' in cb25):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb26 = request.POST.getlist("Non-Fiction")
	if('on' in cb26):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb27 = request.POST.getlist("Fiction")
	if('on' in cb27):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb28 = request.POST.getlist("Physical")
	if('on' in cb28):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb29 = request.POST.getlist("Mental")
	if('on' in cb29):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb30 = request.POST.getlist("Economics")
	if('on' in cb30):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb31 = request.POST.getlist("Entrepeneurship")
	if('on' in cb31):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb32 = request.POST.getlist("Black and White")
	if('on' in cb32):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb33 = request.POST.getlist("Color")
	if('on' in cb33):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb34 = request.POST.getlist("Auditing")
	if('on' in cb34):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb35 = request.POST.getlist("Taxes")
	if('on' in cb35):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb36 = request.POST.getlist("Documents")
	if('on' in cb36):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb37 = request.POST.getlist("Images")
	if('on' in cb37):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb38 = request.POST.getlist("Body Building")
	if('on' in cb38):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb39 = request.POST.getlist("Weight Loss")
	if('on' in cb39):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb40 = request.POST.getlist("Personal Trainer")
	if('on' in cb40):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb41 = request.POST.getlist("Employment counsellor")
	if('on' in cb41):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb42 = request.POST.getlist("Resume")
	if('on' in cb42):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb43 = request.POST.getlist("Speaking")
	if('on' in cb43):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)
	cb44 = request.POST.getlist("Writing")
	if('on' in cb44):
		CheckBoxes.append(True)
	else:
		CheckBoxes.append(False)

	toDisplay = []
	skillString = ""
	for x in xrange(44) :
		if CheckBoxes[x] == True:
			toDisplay.append(allInterests[x])
			if(x != 0):
				skillString += ","
			skillString += allInterests[x]

	new_interests = Interest(username=request.user.username,
		interestList=json.dumps(toDisplay));
	new_interests.save();


	Person.objects.filter(usernames=request.user.username).update(
		skills=skillString);
	Guru.objects.filter(user=request.user).update(skills=skillString)
	context = [];
	return redirect(reverse('home'))

@login_required
def updateInterests(request):
	saveInterests(request)
	return redirect(reverse('home'))

@login_required
def search(request):
	context = {}
	guru = Guru.objects.get(user=request.user)
	context['currUser'] = request.user
	context['image'] = guru.picture
	if not 'q' in request.POST or not request.POST['q']:
		return redirect(reverse('home')) # shouldnt happen
	query = request.POST['q']
	##search by username and then by skill
	userMatches = Person.objects.filter(usernames=query)
	skillMatches = Person.objects.filter(skills__icontains=query)
	if skillMatches:
		context['results'] = skillMatches
	if userMatches:
		context['results'] = userMatches
	return render(request, 'guru/search.html', context)

@login_required
def get_relevantInterest(request):
	matches = Listing.objects.filter(skillType="None");

	toDisplay = json.loads(Interest.objects.get(
		username=request.user.username).interestList)
	for x in xrange(len(toDisplay)):
		matches = matches | Listing.objects.filter(skillType=toDisplay[x])


	d = dict()
	print(matches)
	for match in matches:
		da = dict()
		da['subject'] = match.subject
		da['location'] = match.location
		da['description'] = match.description
		da['userId'] = match.guru.user.id
		da['firstName'] = match.guru.user.first_name
		da['lastName'] = match.guru.user.last_name
		da['username'] = match.guru.user.username
		da['rating'] = match.guru.rating
		da['picture'] = match.guru.picture.url
		da['date'] = match.date.strftime("%m-%d-%Y %H:%M")
		da['skillType'] = match.skillType
		d[match.id] = da
	
	return HttpResponse(json.dumps(d), content_type="application/json")