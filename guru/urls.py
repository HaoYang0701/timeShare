from django.conf.urls import include, url, patterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', 'guru.views.home', name='home'),
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'guru/login.html'}, name='login'),
    url(r'^logout$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^register$', 'guru.views.register', name='register'),
    url(r'^inbox$', 'guru.views.inbox', name='inbox'),
    url(r'^reminders$', 'guru.views.reminders', name='reminders'),
    url(r'^calendar$', 'guru.views.calendar', name='calendar'),
    url(r'^myreviews$', 'guru.views.myreviews', name='myreviews'),
    url(r'^settings$', 'guru.views.settings', name='settings'),
    url(r'^searchresults$', 'guru.views.searchresults', name='searchresults'),
    url(r'^postdetails/(?P<id>\d+)$', 'guru.views.postdetails', name='postdetails'),
    url(r'^profile/(?P<id>\d+)$', 'guru.views.profile', name='profile'),
    url(r'^profile/(?P<username>\w+)$', 'guru.views.pprofile', name='pprofile'),
    url(r'^editprofile', 'guru.views.editprofile', name='editprofile'),
    url(r'^newuser$', 'guru.views.createNewUser', name='newuser'),
    url(r'^reset$', 'guru.views.reset', name='resetpasswordrender'),
    url(r'^resetpassword$', 'guru.views.resetpassword', name='resetpassword'),
    url(r'^newlisting$', 'guru.views.newListing', name='newlisting'),
    url(r'^Interest$', 'guru.views.addInterests', name='addInterests'),
    url(r'^alllistings$', 'guru.views.allListings', name='allListings'),
    url(r'^addlisting$', 'guru.views.addlisting', name='addlisting'),
    url(r'^compose$', 'guru.views.compose', name='compose'),
    url(r'^compose/(?P<id>\d+)$', 'guru.views.lcompose', name='lcompose'),
    url(r'getusernames$', 'guru.views.getusernames', name='getusernames'),
    url(r'sendmessage$', 'guru.views.sendmessage', name='sendmessage'),
    url(r'sendreply$', 'guru.views.sendreply', name='sendreply'),
    url(r'^message/(?P<id>\d+)$', 'guru.views.messageExpanded', name='messageExpanded'),
    url(r'^interested/(?P<id>\d+)$', 'guru.views.interested', name='interested'),
    url(r'^uninterested/(?P<id>\d+)$', 'guru.views.uninterested', name='uninterested'),
    url(r'^activity$', 'guru.views.activity', name='activity'),
    url(r'^dismiss-request/(?P<reqInfo>\w+)$', 'guru.views.dismissRequest', name='dismissRequest'),
    url(r'^confirm-request$', 'guru.views.confirmRequest', name='confirmRequest'),
    url(r'^saveInterests$', 'guru.views.saveInterests', name='saveInterests'),
    url(r'^schedule/(?P<listingId>\d+)/(?P<guruId>\d+)$', 'guru.views.schedule', name='schedule'),
    url(r'^schedule/(?P<listingId>\d+)$', 'guru.views.studentSchedule', name='studentSchedule'),
    url(r'^add-date$', 'guru.views.add_date', name='addDate'),
    url(r'^delete-date/(?P<id>\d+)$', 'guru.views.delete_date', name='deleteDate'),
    url(r'^get-dates$', 'guru.views.get_dates', name='getDates'),
    url(r'^confirm-date$', 'guru.views.confirm_date', name='confirmDate'),
    url(r'^dismiss-sched$', 'guru.views.dismiss_sched', name='dismissSched'),
    url(r'^confirm-sched$', 'guru.views.confirm_sched', name='confirmSched'),
    url(r'^updateInterests$', 'guru.views.updateInterests', name='updateInterests'),
    url(r'^review/(?P<sessionId>\d+)$', 'guru.views.reviewSession', name='reviewSession'),
    url(r'^postReview$', 'guru.views.postReview', name='postReview'),
    url(r'getcategories$', 'guru.views.getcategories', name='getcategories'),
    url(r'sendtext$', 'guru.views.sendtext', name='sendtext'),
    url(r'search$', 'guru.views.search', name='search'),
    url(r'^get-relevantInterest$', 'guru.views.get_relevantInterest', name='getrelevantInterest'),
]

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))