'''
This is a "hello world" flask webpage.
During the last 2 weeks of class,
we will be modifying this file to demonstrate all of flask's capabilities.
This file will also serve as "starter code" for your Project 5 Twitter webpage.

NOTE:
the module flask is not built-in to python,
so you must run pip install in order to get it.
After doing do, this file should "just work".
'''

from crypt import methods
import datetime
from time import time
from tkinter.tix import Tree
from flask import Flask, render_template, request, make_response
app = Flask(__name__)

# anything that starts with a @ is called a "decorator" in python
# in general, decorators modify the functions that follow them
@app.route('/')     
def root():
    print_debug_info()
    '''
    text = 'hello friend!'
    text = '<strong>' + text + '</strong>' # + 100
    return text
    '''
    messages = [{}]

    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # render_template does preprocessing of the input html file;
    # technically, the input to the render_template function is in a language called jinja2
    # the output of render_template is html
    return render_template('root.html', logged_in=good_credentials, messages=messages)


def print_debug_info():
    # GET method
    print('request.args.get("username")=', request.args.get("username"))
    print('request.args.get("password")=', request.args.get("password"))

    # POST method
    print('request.form.get("username")=', request.form.get("username"))
    print('request.form.get("password")=', request.form.get("password"))

    # cookies
    print('request.cookies.get("username")=', request.cookies.get("username"))
    print('request.cookies.get("password")=', request.cookies.get("password"))


def are_credentials_good(username, password):
    # FIXME:
    # look inside the databasse and check if the password is correct for the user
    if username == 'haxor' and password == '1337':
        return True
    else:
        return False


@app.route('/login', methods=['GET', 'POST'])     
def login():
    print_debug_info()
    # requests (plural) library for downloading;
    # now we need request singular 
    username = request.form.get('username')
    password = request.form.get('password')
    print('username=', username)
    print('password=', password)

    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # the first time we've visited, no form submission
    if username is None:
        return render_template('login.html', bad_credentials=False)

    # they submitted a form; we're on the POST method
    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:
            # if we get here, then we're logged in
            #return 'login successful'
            
            # create a cookie that contains the username/password info
            template = render_template(
                'logged.html', 
                bad_credentials=False,
                logged_in=True,
                username=username)
            
            #return template
            response = make_response(template)
            response.set_cookie('username', username)
            response.set_cookie('password', password)
            return response

# scheme://hostname/path
# the @app.route defines the path
# the hostname and scheme are given to you in the output of the triangle button
# for settings, the url is http://127.0.0.1:5000/logout to get this route
@app.route('/logout')     
def logout():
    print_debug_info()
    # 'error' # this will throw an error
    
    template = render_template(
            'root.html',
            bad_credentials=True,
            logged_in=False
    )
    #return template
    response = make_response(template)
    response.set_cookie('username', '')
    response.set_cookie('password', '')
    return response

# 403 error code

@app.route('/create_message', methods=['GET', 'POST'])
def create_message():
    # Attempt to get the message from form data regardless of the request method
    message = request.form.get('message')
    timestamp = datetime.datetime.utcnow()

    # Only process if message is not None, meaning a form has been submitted
    if message:
        print(f"Message: {message}")
        print(f"Time: {timestamp}")

        # Assuming you do some processing here, like saving to a database
        # and then you might want to redirect or render a different template
        return render_template('test.html', message=message, timestamp=timestamp)
    
    # If no message, it's likely a GET request or no data submitted, so show the form
    return render_template('create_message.html')

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    username = request.form.get('username')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    
    # the first time we've visited, no form submission
    if username is None:
        return render_template('create_user.html')
    
    else:
        # Extract data from form
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        # Here you would add logic to verify the passwords match
        # and handle the creation of a new user, possibly saving to a database

        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Password Confirm: {password_confirm}")
        
        template = render_template(
                'logged.html', 
                bad_credentials=False,
                logged_in=True,
                username=username)
        
        response = make_response(template)
        # Redirect to another page, perhaps a confirmation page
        return response

app.run(port=1328)
