from flask import Flask, render_template, redirect, url_for, request, g, session
import sqlite3
from functools import wraps
from time import sleep
app = Flask(__name__)
db_users_location = 'data/users.db'
db_posts_location = 'data/posts.db'
app.secret_key = 'kljjkl;;kll;kl;kk345756l;kl;solheroushdflkgm;mlgjk'
#cheking tht the user has loged in
def requires_login(f):
        @wraps(f)
        def decorated(*args, **kwargs):
                status = session.get('logged_in', False)
                if not status:
                        return redirect(url_for('.index'))
                return f(*args, **kwargs)
        return decorated
#loging the user out
@app.route('/logout')
def logout():
	session['logged_in'] = False
	return redirect(url_for('index'))

#connect to the users database
def get_users_db():
	db = getattr(g, 'db', None)
	if db is None:
		db = sqlite3.connect(db_users_location)
		g.db = db
	return db
#connect to the post database
def get_post_db():
        db = getattr(g, 'db', None)
        if db is None:
                db = sqlite3.connect(db_posts_location)
                g.db = db
        return db
#closes the user database
@app.teardown_appcontext
def close_users_db_connection(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()
#closes the post database
@app.teardown_appcontext
def close_post_db_connection(exception):
        db = getattr(g, 'db', None)
        if db is not None:
                db.close()
#initialise the users database
def init_users_db():
	with app.app_context():
		db = get_users_db()
		with app.open_resource('data/users.sql',mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()
#initialise the posts database
def init_post_db():
        with app.app_context():
                db = get_post_db()
                with app.open_resource('data/posts.sql',mode='r') as f:
			db.cursor().executescript(f.read())
                db.commit()
# loged in page
@app.route("/Logged", methods = ['GET', 'POST'])
@requires_login
def logged():
	posts =	[]
	name = session.get('name')
	db = get_post_db()
	return render_template("Logged.html",name=name,posts=posts,db=db)

# where the user make the post 
@app.route("/Post", methods = ['GET', 'POST'])
@requires_login
def post():
	error = None
	db = get_post_db()
	name = session.get('name')
	if request.method == 'POST':
		if request.form['post'].replace(" ","") == "" :
			error = "Can't make empty post!"
		else:
			db.cursor().execute('insert into posts values("'+name+'", "'+request.form['post']+'")')
			db.commit()
			return redirect((url_for('logged')))
        return render_template("Post.html", name=name,error=error)


# this is the main page
@app.route("/", methods = ['GET', 'POST'])
def index():
	validation = None
	if request.method == 'POST':
		db = get_users_db()
        	for row in db.cursor().execute("SELECT name FROM users WHERE name='"+request.form['username']+"' and password='"+request.form['password']+"'"):
			validation = "1"
		if validation != "1" :
			validation = "Login failed, pleace try again"
		else:
			session['logged_in'] = True
			session['name'] = request.form['username']
			return redirect(url_for('logged'))
	dbp = get_post_db()
	return render_template("Index.html", validation=validation,dbp=dbp )

# the register site
@app.route("/Register", methods = ['GET', 'POST'])
def Register():
	db = get_users_db()
	errorname = None
	errorpassword = None
	erroremail = None
	suc = None
	if request.method == 'POST':
		if request.form['username'] == "":
			errorname = 'Pleace type a name'
		else:
			for row in db.cursor().execute("SELECT name FROM users WHERE name='"+request.form['username']+"'"):
				if str(row) == "(u'"+request.form['username']+"',)":
					errorname = "Name is taken!"
			if errorname != None:
					errorname = "Name is taken!"
			else:
				if request.form['password'] == "":
					errorpassword = 'Password Missing'
				else:
					if request.form['password'] != request.form['Repassword']:
						errorpassword = 'Password Dasnt Match'
					else:
						if request.form['email'] == "":
							erroremail = 'Email is missing'
						else:
							db.cursor().execute('insert into users values("'+request.form['username']+'", "'+request.form['password']+'", "'+request.form['email']+'")')
							db.commit()
							suc = 'Registration sucssesfull!'
	return render_template("Register.html", errorname=errorname, errorpassword=errorpassword, erroremail=erroremail, suc=suc)

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)

