from django.forms import ModelForm
from guru.models import *
from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.Form):
	email = forms.EmailField(max_length=40)
	username = forms.CharField(max_length=20)
	password = forms.CharField(widget=forms.PasswordInput())
	confirmpassword = forms.CharField(widget=forms.PasswordInput())
	firstname = forms.CharField(max_length=20)
	lastname = forms.CharField(max_length=20)

	def clean(self):
		cleaned_data = super(RegistrationForm, self).clean()
		email = cleaned_data.get('email')
		username = cleaned_data.get('username')
		password = cleaned_data.get('password')
		confirmpassword = cleaned_data.get('confirmpassword')
		
		if password != confirmpassword:
			raise forms.ValidationError("passwords does not match")
		if email and User.objects.filter(email__exact=email):
			raise forms.ValidationError("email is already taken")
		if username and User.objects.filter(username__exact=username):
			raise forms.ValidationError("username already taken")
		return cleaned_data

class ResetForm(forms.Form):
	email = forms.EmailField(max_length=40)
	def clean(self):
		cleaned_data = super(ResetForm, self).clean()
		cleanEmail = cleaned_data.get('email') #only need to check if email exists
		if( cleanEmail and User.objects.filter(email=cleanEmail).count() != 1):
			raise forms.ValidationError("Email not registered")
		return cleaned_data

class EditProfileForm(forms.ModelForm):
	class Meta:
		model = Guru
		exclude = ('user', )
		fields = ['location', 'skills', 'age', 'bio', 'picture']
		widgets = {'picture' : forms.FileInput() }
	
	def clean(self): #nothing besides age needs to be cleaned
		cleaned_data = super(EditProfileForm, self).clean()
		age = cleaned_data.get('age') 
		if( age < 5 or age > 120): #check age range
			raise forms.ValidationError("Please enter a valid age")
		return cleaned_data

class ListingForm(forms.ModelForm):
	class Meta:
		model = Listing
		fields = ['subject','location','description']
	def clean(self):
		cleaned_data = super(ListingForm, self).clean()
		#nothing much to clean except checking size of input non-null
		subj = cleaned_data.get('subject')
		if (len(subj) < 1):
			raise forms.ValidationError("Subject must not be empty")
		location = cleaned_data.get('location')
		if (len(location) < 1):
			raise forms.ValidationError("location must not be empty")
		description = cleaned_data.get('description')
		if (len(description) < 1):
			raise forms.ValidationError("description must not be empty")
		return cleaned_data


class PersonForm(forms.ModelForm):
	class Meta:
		model = Person #Form used for search engine, no need for cleaning
		fields = ('usernames',)
		

