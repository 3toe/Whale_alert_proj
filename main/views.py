from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, NumeralTickFormatter
from decouple import config
import bcrypt
import datetime
import requests
import calendar
import numpy as np
from math import radians
from statistics import mode

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
   # create the currencies instances if none exist yet:
   if not Currency.objects.all().exists():
      Currency.object.create(name="Bitcoin", symbol="btc")
      Currency.object.create(name="Ethereum", symbol="eth")
      Currency.object.create(name="Ripple", symbol="xrp")
      Currency.object.create(name="Tether", symbol="usdt")
      Currency.object.create(name="Binance", symbol="busd")
   #create the new user and auto fave Bitcoin
   User.objects.create(alias = request.POST['alias'], password = pw_hash, email = request.POST['email'])
   user = User.objects.filter(email=request.POST['email'])
   user[0].fav_currency.set([Currency.objects.get(id=1)])
   user[0].save()
   # store user's name and id in session to access later:
   if user:
      logged_in = user[0]
      request.session['user_id'] = logged_in.id
   # access granted if all is well:
   return redirect('/mainpage')

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
         request.session['user_id'] = logged_in.id
         # access granted if all is well:
         return redirect('/mainpage')
   # error message if the login credentials aren't in the db
   messages.error(request, "Your username or password is incorrect.")
   return redirect('/')

# POST request to log user out upon log-out request.
def logout(request):
   # upon logout, flush the session and go back to reg / login page:
   request.session.flush()
   return redirect('/')

# GET request to render the main page
def mainpage(request):
   # redirect requests to the reg / login page if not logged-in:
   if not 'user_id' in request.session:
      return redirect('/')
   # Get the logged-in user object
   user = User.objects.get(id=request.session['user_id'])

   '''code for API response'''
   # generate unix timestamp for transactions start date
   timestamp = datetime.datetime.utcnow()
   lookback = 3600
   utc_timestart = calendar.timegm(timestamp.utctimetuple()) - lookback
   # Get API data
   baseURL = 'https://api.whale-alert.io/v1/transactions?api_key='
   key = config('API_KEY')
   min_val = '&min_value=500000'
   starttime = '&start=' + str(utc_timestart+5) # +5 to avoid delays in this request causing us to extend over the 1-hour limit with the free API account
   # get API response data (and print error code)
   response = requests.get(baseURL + key + min_val + starttime)
   print(response)

   '''code for graphing'''
   # initialize bokeh graph components
   div = []
   script = []
   # define a function that will work our data into a dictionary Bokeh can use:
   def stacker(ts, tx):
      #create x axis list
      xlist = list(dict.fromkeys(ts))
      # initialize y list and iterator list
      ylist = []
      i_list = []
      # nested loops to separate transaction lists
      for x in xlist:
         for i in range(len(ts)):
            if x == ts[i]:
                  i_list.append(tx[i])
         ylist.append(i_list)
         i_list =[]
      # establish count of lists
      modeVal = mode(ts)
      num_layers = ts.count(modeVal)
      mod_ylist = []
      # fill in 0's for empty layers
      for element in ylist:
         mod_ylist.append(element+[0]*(num_layers - len(element)))
      # transpose arrays with numpy
      final = np.array(mod_ylist).T
      # add lists to dict
      data = {'xlist' : xlist}
      for i in range(len(final)):
         data['layer' + str(i)] = final[i].tolist()
      return data
   
   # get ts and tx lists for coins we care about:
   for coin in user.fav_currency.all():
      ts = [datetime.datetime.fromtimestamp(utc_timestart)]
      # ts = [utc_timestart]
      tx = [0]
      for APIdata in response.json()['transactions']:
         if APIdata['symbol'] == coin.symbol:
            ts.append(datetime.datetime.fromtimestamp(APIdata['timestamp']))
            # ts.append(APIdata['timestamp'])
            tx.append(APIdata['amount_usd'])
      #stack data for the graph
      graphdata = stacker(ts, tx)
      # get data layer names
      ylayers = list(graphdata.keys())
      ylayers.pop(0)
      # generate orangey colors for each layer
      colors = []
      for i in range(len(ylayers)):
         if i < 30:
            color = "#" + (hex(int(0xdda0)-i*1500)[2:]) + "00"
            colors.append(color)
         elif i >= 60:
            colors.append(colors[i-60])
         elif i >= 30:
            colors.append(colors[i-30])
      # set up data for bokeh standard
      source = ColumnDataSource(graphdata)
      # create graph object
      f = figure(x_axis_type="datetime", width=550, height=260, title=str(coin.symbol).upper() + " transactions (USD)", tooltips="$y", background_fill_alpha = 0.3)
      f.vbar_stack(ylayers, x='xlist', width = 25000, color = colors, source = source)
      '''style graphs'''
      # x axis formatting
      date_pattern = ["%Y-%m-%d\n%H:%M"]
      f.xaxis.formatter = DatetimeTickFormatter(
      seconds=date_pattern,
      minsec=date_pattern,
      minutes=date_pattern,
      hourmin=date_pattern,
      hours=date_pattern,
      days=date_pattern,
      months=date_pattern,
      years=date_pattern,
      )
      f.xaxis.major_label_orientation = radians(45)
      f.xaxis.major_label_text_color = "#eeeeee"
      f.xaxis.axis_label = "date / time"
      f.xaxis.axis_label_text_color = "#c0c317"
      # y axis formatting
      f.yaxis.formatter = NumeralTickFormatter(format="$0,000,000")
      f.yaxis.major_label_text_color = "#eeeeee"
      f.yaxis.axis_label = "Amount USD"
      f.yaxis.axis_label_text_color = "#c0c317"
      f.y_range.start = 0
      # other formatting
      f.border_fill_alpha = 0.2
      f.title.text_color = "#c0c317"
      # break out components to add to html file
      s, d = components(f)
      # add components to lists
      script.append(s)
      div.append(d)
   '''end graphing code'''  
   # Send data to template
   context = {
      "CoinList" : Currency.objects.all(),
      "User" : User.objects.get(id=request.session['user_id']),
      "Scripts" : script,
      "Divs" : div
   }
   return render(request, 'mainpage.html', context)

# POST from form to select for which coins the user wants to see data.
def changecoins(request):
   # redirect if someone trying to bypass login:
   if request.method == 'GET':
      return redirect('/')
   # update user's favorite coins here
   user = User.objects.get(id=request.session['user_id'])
   for coin in Currency.objects.all():
      # use try/except because unchecked ckb's don't send anything
      try:
         request.POST[str(coin.id)]
         user.fav_currency.add(Currency.objects.get(id=coin.id))
         user.save()
      except:
         user.fav_currency.remove(Currency.objects.get(id=coin.id))
         user.save()
   return redirect('/mainpage')

def deluser(request):
   # redirect if someone trying to bypass login:
   if request.method == 'GET':
      return redirect('/')
   # delete logged-in user
   user = User.objects.get(id=request.session['user_id'])
   user.objects.delete()
   request.session.flush()
   return redirect('/')