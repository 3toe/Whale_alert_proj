A final project for my Coding Dojo boot camp that integrates:

 - Django 2.2 with login and auth (using bcrypt)
 - API calls
 - Bokeh data visualization
 - ORM

to visualize live data from the API and filter it based on user preferences before delivery.

rev 1: see test.py for working changes.
rev 2: deleted test.py (oops). Added graphing functionality.
future rev: I initially wanted to have streaming data, but I could not get the async websocket stuff working in time.

As is, the project uses user and currency models, with a many-to-many relationship that is user-customizable.
Once those relationships are set, the logic sends a request to the API, parses through the response's json data for relevant transaction info,
manipulates it into a format Bokeh can use, creates the custom stacked bar graphs, and delivers that to our template to render.

libraries used (aside from Django):
Bokeh
numpy
bcrypt
python-decouple
datetime and calendar
math
requests
statistics
regex

For a view of this, please see my video walk-through.  The code is commented for more in-depth review. most of the logic is in main/views.py
https://youtu.be/IMUftkmTmSw