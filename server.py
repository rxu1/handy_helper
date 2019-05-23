from flask import Flask, render_template, session, redirect, request, flash
import re #importing the regex module
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL

app = Flask(__name__, template_folder="templates")
app.secret_key = "The secrest biz u ever seent"
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# BIRTHDAY_REGEX = re.compile(r'^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$')

def login_user(user_info, session_object):
    session_object['curr_user_id'] = user_info['id']
    session_object['curr_user_name'] = user_info['name']

@app.route('/')
def show_login():
    print("*"*80)
    print("in the show_login function")
    return render_template ("login.html")

@app.route('/home')
def show_home():
    print("*"*80)
    print("in the show_home function")
    if not 'curr_user_id' in session:
        return redirect("/")
    else:
        logged_in_user = {
            'name': session['curr_user_name'],
            'id': session['curr_user_id']
        }
        print(logged_in_user)
        print(logged_in_user['id'])
        print("*"*50)
        # query to select user data for first name to then place into Welcome section of home.html
        mysql = connectToMySQL("jobs")
        users_query = "SELECT * FROM users;"
        users = mysql.query_db(users_query)
        context = {
            'user': logged_in_user,
            'users': users,
        }

        mysql = connectToMySQL("jobs")
        jobs_query = "SELECT * FROM users JOIN jobs ON jobs.user_id = users.id WHERE users.id != %(user_id)s;"
        data ={
            "user_id": session['curr_user_id'],
        }
        jobs = mysql.query_db(jobs_query, data)
        context2 = {
            'jobs' : jobs,
        }

        mysql = connectToMySQL("jobs")
        jobs1_query = "SELECT * FROM users JOIN jobs ON jobs.user_id = users.id WHERE users.id = %(user_id)s;"
        data = {
            'user_id': session['curr_user_id'],
        }
        users = mysql.query_db(jobs1_query, data)
        context3 = {
            'user' : users,
        }
    #passing in variables with render template allows these values to be accessed in html document
    return render_template ("home.html", context=context, context2=context2, context3=context3)

@app.route('/job/new')
def show_new_job():
    print("*"*80)
    print("in the show_new_job function")
    if not 'curr_user_id' in session:
        return redirect("/")

    logged_in_user = {
        'name': session['curr_user_name'],
        'id': session['curr_user_id']
    }
    print(logged_in_user)
    #same query to get first_name into the welcome portion of the html
    mysql = connectToMySQL("jobs")
    users_query = "SELECT * FROM users;"
    users = mysql.query_db(users_query)
    context = {
        'user': logged_in_user,
        'users': users,
    }
    return render_template ("new_job.html", context=context)

@app.route('/job/edit/<job_id>')
def show_edit_job(job_id):
    print("*"*80)
    print("in the show_edit_job function")
    if not 'curr_user_id' in session:
        return redirect("/")
    else:
        logged_in_user = {
            'name': session['curr_user_name'],
            'id': session['curr_user_id']
        }
        # print(logged_in_user)
        print(logged_in_user['id'])

        # this sql is to insert the first name into edit_job template
        mysql = connectToMySQL("jobs")
        users_query = "SELECT * FROM users;"
        users = mysql.query_db(users_query)
        print(users)
        context = {
            'user': logged_in_user,
            'users': users,
        }
        # query allows the edit form to prepopulate with values from that specific job
        mysql = connectToMySQL("jobs")
        job_query = "SELECT * FROM jobs WHERE jobs.id = %(job_id)s;"
        data = {
            'job_id':job_id,
        }
        jobs = mysql.query_db(job_query, data)
        print(jobs)
        context2 = {
            'job': jobs,
        }
        return render_template ("edit_job.html", context=context, context2=context2)


@app.route('/job/<job_id>')
def show_job_details(job_id):
    print("*"*80)
    print("in the show_job_details function")
    if not 'curr_user_id' in session:
        return redirect("/")

    logged_in_user = {
        'name': session['curr_user_name'],
        'id': session['curr_user_id']
    }
    print(logged_in_user)
    print(logged_in_user['id'])

    mysql = connectToMySQL("jobs")
    job_query = "SELECT * FROM users JOIN jobs ON jobs.user_id = users.id WHERE jobs.id = %(job_id)s;"
    data = {
        'job_id': job_id,
    }
    jobs = mysql.query_db(job_query, data)
    context = {
        'jobs': jobs,
    }

    mysql = connectToMySQL("jobs")
    users_query = "SELECT first_name FROM users;"
    users = mysql.query_db(users_query)
    print(users)
    context2 = {
        'user': logged_in_user,
        'users': users,
    }
    return render_template ("job_details.html", context=context, context2=context2)

@app.route('/logout')
def logout():
    print("*"*80)
    print("logging out")
    session.clear()
    return redirect("/")

@app.route("/register", methods=["POST"])
def register():
    print("*"*80)
    print(request.form)
    error_messages = []
    # check validations
    if not request.form['first_name'].isalpha(): #returns a boolean that shows whether a string contains only alphabetic characters
        error_messages.append("First name must be alphabetic characters!")
    if len(request.form['first_name']) < 2:
        error_messages.append("First name must be longer than two characters!")
    if len(request.form['last_name']) < 2:
        error_messages.append("Last name needs to be longer than two characters!")
    if not EMAIL_REGEX.match(request.form['email']): #test whether a field matches the email pattern
        error_messages.append("Email must follow format name@email.com")
    if request.form['password'] != request.form['confirm_password']:
        error_messages.append("Passwords don't match")
    if len(request.form['confirm_password']) < 2:
        error_messages.append("Passwords don't match")
    if len(request.form['password']) < 2:
        error_messages.append("Password must be longer than two characters")

    if len(error_messages) == 0:
        # log our user in...
        pw_hash = bcrypt.generate_password_hash(request.form['password']) #creates a password hash
        mysql = connectToMySQL("jobs")
        query = "INSERT INTO users (first_name, last_name, email, password_hash, created_at, updated_at) VALUES (%(first)s, %(last)s, %(email)s, %(password)s, NOW(), NOW());"
        data = {
            'first': request.form['first_name'],
            'last': request.form['last_name'],
            'email': request.form['email'],
            'password': pw_hash,
        }
        results = mysql.query_db(query, data)
        print(results)
        login_user({'id': results, 'name': request.form['first_name']}, session)
        return redirect("/home")
    else:
        # flash a bunch of messages
        for message in error_messages:
            print(message)
            flash(message)
        return redirect("/")

@app.route("/login", methods= ['POST'])
def login():
    errors = []
    # grab deetz
    input_pw = request.form['password']
    input_email = request.form['email']
    # see if user exists
    mysql = connectToMySQL("jobs")
    query = "SELECT * FROM users WHERE(email = %(email)s)"
    data = {
        'email': input_email
    }
    result = mysql.query_db(query, data)
    if len(result) is not 1:
        errors.append("Email is incorrect!")
    else:
        if not bcrypt.check_password_hash(result[0]['password_hash'], input_pw):
            errors.append("Password is incorrect!")
        else:
            login_user({'id': result[0]['id'], 'name':result[0]['first_name']}, session)
            print(session)
    if len(errors) == 0:
        return redirect("/home")
    else:
        flash("Incorrect login")
        return redirect("/")

@app.route("/job/submit", methods=['POST'])
def submit_job():
    print("*"*80)
    print("in submit_job function")
    print(request.form)
    if not 'curr_user_id' in session:
        return redirect("/")

    error_messages = []

    if len(request.form['title']) < 3:
        error_messages.append("Title must be at least three characters long!")
    if len(request.form['description']) < 3:
        error_messages.append("Description must be at least three characters long!")
    if len(request.form['location']) < 3:
        error_messages.append("Location must be at least three characters long!")

    if len(error_messages) == 0:
        logged_in_user = {
            'name': session['curr_user_name'],
            'id': session['curr_user_id'],
        }
        # query to insert form data for new job in db
        mysql = connectToMySQL("jobs")
        query = "INSERT INTO jobs (user_id, title, description, location, created_at, updated_at) VALUES (%(user_id)s, %(title)s, %(desc)s, %(loc)s, NOW(), NOW());"
        data={
            'user_id' : session['curr_user_id'],
            'title': request.form['title'],
            'desc': request.form['description'],
            'loc': request.form['location'],
        }
        print(data)
        job_results = mysql.query_db(query, data)
        print(job_results)
        return redirect('/home')
    else:
        for message in error_messages:
            print(message)
            flash(message)
        return redirect("/job/new")

@app.route("/edit/job/<job_id>", methods=["POST"])
def edit_job(job_id):
    print("*"*80)
    print("in edit_job function")
    print(request.form)
    if not 'curr_user_id' in session:
        return redirect("/")

    error_messages = []
    if len(request.form['title']) < 3:
        error_messages.append("Title must be at least three characters long!")
    if len(request.form['description']) < 3:
        error_messages.append("Description must be at least three characters long!")
    if len(request.form['location']) < 3:
        error_messages.append("Location must be at least three characters long!")

    if len(error_messages) == 0:
        logged_in_user = {
            'name': session['curr_user_name'],
            'id': session['curr_user_id'],
        }
        mysql = connectToMySQL("jobs")
        query = "UPDATE jobs SET user_id = %(user_id)s, title = %(title)s, description = %(desc)s, location = %(loc)s WHERE id = %(job_id)s;"
        data = {
            'user_id' : session['curr_user_id'],
            'job_id': job_id,
            'title': request.form['title'],
            'desc': request.form['description'],
            'loc': request.form['location'],
        }
        edit_job = mysql.query_db(query, data)
        print(edit_job)
        return redirect("/home")
    else:
        for message in error_messages:
            print(message)
            flash(message)
        # for redirects, you must use a string OR
        # return redirect(f"/job/edit/{job_id}")
        return redirect('/job/edit/'+job_id)

@app.route('/delete/<job_id>', methods=["POST"])
def delete_job(job_id):
    print("*"*80)
    print("in the show_trip_details function")
    if not 'curr_user_id' in session:
        return redirect("/")

    logged_in_user = {
        'name': session['curr_user_name'],
        'id': session['curr_user_id']
    }
    print("*"*50)

    mysql = connectToMySQL('jobs')
    query = "DELETE FROM jobs WHERE id = %(job_id)s;"
    data = {
        "job_id" : job_id,
    }
    delete_job = mysql.query_db(query, data)
    print(delete_job)
    return redirect('/home')


if __name__=="__main__":
    app.run(debug=True)
