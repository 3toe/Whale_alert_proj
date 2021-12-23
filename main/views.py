from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
import bcrypt

# GET method returning the index page render
def index(request):
   return render(request, 'index.html')

# POST method for the registration, with an if for success/fail
def reg(request):
   # redirect if someone trying to bypass login:
   if request.method == 'GET':
      return redirect('/')
   # display errors if there are any and go back to login/reg page:
   errors = User.objects.UserValidator(request.POST)
   if len(errors) > 0:
      for key, value in errors.items():
         messages.error(request, value)
      return redirect('/')
   # hash password with bcrypt
   pw_hash = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
   # create the user's db entry
   User.objects.create(alias = request.POST['alias'], password = pw_hash, email = request.POST['email'])
   user = User.objects.filter(email=request.POST['email'])
   # store user's name and id in session to access later:
   if user:
      logged_in = user[0]
      request.session['alias'] = logged_in.alias
      request.session['user_id'] = logged_in.id
   # access granted if all is well:
   return redirect('/main')

# POST method for the login, with an if for success/fail
def login(request):
   # redirect if someone trying to bypass login:
   if request.method == 'GET':
      return redirect('/')
   # check if email address entered exists in db, if not redirect to reg/login page:
   user = User.objects.filter(email=request.POST['email'])
   if user:
      logged_in = user[0]
      # if the user is found, check their hashed PW against the db hashed PW, error if needed:
      if bcrypt.checkpw(request.POST['password'].encode(), logged_in.password.encode()):
         request.session['alias'] = logged_in.alias
         request.session['userid'] = logged_in.id
         # access granted if all is well:
         return redirect('/main')
   # error message if the login credentials aren't in the db
   messages.error(request, "Your username or password is incorrect.")
   return redirect('/')

# POST request to log user out upon log-out request.
def logout(request):
   # upon logout, flush the session and go back to reg / login page:
   request.session.flush()
   return redirect('/')

