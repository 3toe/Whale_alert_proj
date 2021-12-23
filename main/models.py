from django.db import models
import re

class LoginManager(models.Manager):
   def UserValidator(self, postData):
      errors = {}
      if len(postData['alias']) < 4:
         errors['alias'] = "Your alias should be at least 4 characters."
      EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
      if not EMAIL_REGEX.match(postData['email']):           
         errors['email'] = "Email address is required and with proper A@B.XYZ format."  
      if User.objects.filter(email=postData['email']):
         errors['emailreg'] = "The email address entered is already registered."
      if len(postData['password']) < 10:
         errors['passlength'] = "Password must be at least 10 characters."
      if postData['password'] != postData['p2']:
         errors['passmatch'] = "The password and confirmation password did not match."
      return errors

class User(models.Model):
   alias = models.CharField(max_length=255)
   password = models.CharField(max_length=255)
   email = models.CharField(max_length=255)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   objects = LoginManager()

class Currency(models.Model):
   name = models.CharField(max_length=64)
   symbol = models.CharField(max_length=10)
   faved_by = models.ManyToManyField(User, related_name="fav_currencies")
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)