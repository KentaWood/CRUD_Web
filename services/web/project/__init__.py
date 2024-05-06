import os

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    render_template,
    make_response
)

from flask import Flask, jsonify, send_from_directory, request, render_template, make_response,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text  # Ensure text is also imported here
import sqlalchemy
import secrets



app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)
db_connection = "postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev" #how do I change this to go with the enviroment?? 
# db_connection = "postgresql://hello_flask:hello_flask@db:5432/hello_flask_prod"

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email

# anything that starts with a @ is called a "decorator" in python
# in general, decorators modify the functions that follow them
@app.route('/')     
def root():
    print_debug_info()
    
    # Get page number from query parameter (default is 1 if not specified)
    page = request.args.get('page', 1, type=int)

    # Calculate offset for tweets
    offset = (page - 1) * 20

    # Establish a database connection
    engine = create_engine(db_connection)
    connection = engine.connect()

    # SQL query to fetch the 20 most recent tweets, considering the offset
    sql_query = text("""
        SELECT t.text, t.created_at, u.username
        FROM tweets t
        JOIN users u ON t.id_users = u.id_users
        ORDER BY t.created_at DESC
        LIMIT 20 OFFSET :offset;
    """)

    # Execute the query and fetch the results
    result = connection.execute(sql_query, {'offset': offset})
    tweets = result.fetchall()
    connection.close()
    

    # Render the template with tweets
    return render_template('root.html', tweets=tweets, current_page=page)


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
    # Create an SQLAlchemy engine using the specified database connection string
    engine = sqlalchemy.create_engine(db_connection)
    connection = engine.connect()
    
    # Define an SQL query to count the number of records in the 'users' table
    sql_query = text("""
        SELECT COUNT(*) AS user_count
        FROM users
        WHERE username = :username AND password = :password
    """)
    
    # Execute the SQL query with placeholders for username and password
    result = connection.execute(sql_query, {"username": username, "password": password})
    
    # Extract the scalar result (first column of the first row) from the query result
    count = result.scalar()
    
    connection.close()

    # Return True if the count is greater than 0 (credentials are good), False otherwise
    return count > 0


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
                username=username,
                password=password)
            
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

from flask import redirect, url_for, render_template, request
import sqlalchemy
from sqlalchemy import create_engine, text

@app.route('/create_message', methods=['GET', 'POST'])
def create_message():
    # Attempt to get the message from form data
    message = request.form.get('message')
    
    # Getting the username and password from cookies
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    
    # Only process if a message is submitted
    if request.method == 'POST' and message:
        # Create an SQLAlchemy engine using the specified database connection string
        engine = sqlalchemy.create_engine(os.getenv('DATABASE_URL'))
        connection = engine.connect()
        
        # First, confirm that the user's credentials are valid
        user_query = text("""
            SELECT id_users FROM users
            WHERE username = :username AND password = :password
        """)
        user_result = connection.execute(user_query, {"username": username, "password": password}).fetchone()
        
        if user_result:
            user_id = user_result[0]
            # If credentials are good, insert the new tweet
            sql_insert_tweet = text("""
                INSERT INTO tweets (id_users, text, created_at)
                VALUES (:id_users, :text, NOW())
            """)
            connection.execute(sql_insert_tweet, {"id_users": user_id, "text": message})
            connection.commit()
            connection.close()
            
            render_template('create_message.html')
            return redirect(url_for('root'))  # Redirect to the home page to see the new tweet
        else:
            connection.close()
            return render_template('create_message.html', error="Invalid user credentials.")
    
    # If GET request or no data submitted, show the form
    return render_template('create_message.html')


    

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    username = request.form.get('username')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    
    # the first time we've visited, no form submission
    if username is None:
        return render_template('create_user.html')
    
    elif password != password_confirm:
        print("DIFFERENT PASSWORDS")
        return render_template('create_user.html')

    else:
        # Create an SQLAlchemy engine using the specified database connection string
        engine = sqlalchemy.create_engine(db_connection)
        connection = engine.connect()
        
        import secrets

        # Generate a random integer within the specified range
        id_users = secrets.randbits(63)  # 63 bits to fit within the range

        # Add an offset to fit the lower bound of the range
        id_users += 10000000000000

        print(id_users)
        print(username)
        print(password)        

        # Define an SQL query to insert a new user with a random UUID as id_users
        sql_query = text("""
            INSERT INTO users (id_users, username, password)
            VALUES (:id_user, :username, :password)
        """)
        
        
        # sql_query = text("""
        #     INSERT INTO users (id_users, username, password)
        #     VALUES (12321341242124,'test', 'test')
        # """)
        
        print(sql_query)
        
        
        connection.execute(sql_query, {"id_user": id_users ,"username": username, "password": password})
        
        connection.commit()
        # connection.execute(sql_query)
    
        
        connection.close()



        # Here you would add logic to verify the passwords match
        # and handle the creation of a new user, possibly saving to a database
        



                
        template = render_template(
                'logged.html', 
                bad_credentials=False,
                logged_in=True,
                username=username,
                password=password)
        
        #return template
        response = make_response(template)
        response.set_cookie('username', username)
        response.set_cookie('password', password)
        
        return response
    
@app.route('/search', methods=['GET'])
def search():
    # Retrieve the search keyword from the query parameter, defaulting to an empty string if not provided
    keyword = request.args.get('keyword', '')

    # Retrieve the page number, default to 1 if not provided
    page = request.args.get('page', 1, type=int)

    # Calculate the offset for pagination
    offset = (page - 1) * 20

    # Establish a database connection
    engine = create_engine(db_connection)
    connection = engine.connect()

    # SQL query to find tweets containing the keyword, ordered by creation time, and paginated
    # Now includes a join with the users table to fetch the username
    sql_query = text("""
        SELECT t.text, t.created_at, u.username
        FROM tweets t
        JOIN users u ON t.id_users = u.id_users
        WHERE t.text LIKE :keyword
        ORDER BY t.created_at DESC
        LIMIT 20 OFFSET :offset;
    """)

    # Execute the query with placeholders for keyword (wrapped in % for SQL LIKE operation) and offset
    result = connection.execute(sql_query, {'keyword': f'%{keyword}%', 'offset': offset})
    tweets = result.fetchall()
    
    # Calculate the total number of pages based on the total number of matching tweets (for navigation purposes)
    count_query = text("""
        SELECT COUNT(*)
        FROM tweets t
        JOIN users u ON t.id_users = u.id_users
        WHERE t.text LIKE :keyword;
    """)
    count_result = connection.execute(count_query, {'keyword': f'%{keyword}%'})
    total_tweets = count_result.scalar()
    total_pages = (total_tweets + 19) // 20  # Ensures rounding up

    connection.close()
    
    # Render the template with the search results, current page, and total pages
    return render_template('search.html', tweets=tweets, current_page=page, total_pages=total_pages, keyword=keyword)


