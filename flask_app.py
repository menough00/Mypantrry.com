from flask import g, flash, Flask, jsonify, redirect, render_template, request,session
#from flask_sqlalchemy import SQLAlchemy# attempting SQL Alchemy 03/24/21
from sqlalchemy import create_engine, MetaData, Table
#import sqlite3 #removed raw sqlite 3/27/21
import os
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["DEBUG"]=True
app.config["TESTING"]=True
app.config["SECRET_KEY"]="baberuth"
app.config["SESSION_TYPE"]="filesystem"
app.config["SESSION_PERMANENT"]=False

THIS_PATH=os.path.dirname(os.path.abspath(__file__))
DATABASE = "sqlite:///"+ os.path.join(THIS_PATH, "data/my_pantry.db")
print (DATABASE)
db = create_engine(DATABASE, convert_unicode=True)
metadata = MetaData(bind=db)
#db=SQLAlchemy.create_engine("sqlite:///"+DATABASE)# attempting SQL Alchemy 03/24/21
#app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///"+DATABASE
#db=SQLAlchemy(app)


""" removed raw sqlite3 3/27/21
def make_dicts(cur,row):
    # convert the results of the query to a python dictionary
    return dict((cur.description[idx][0],value) for idx,value in enumerate(row))

def get_db():
    #function to retrieve the active Database
    db=getattr(g,"_database",None)
    if db==None:
        db=g._database=sqlite3.connect(DATABASE)
        db.row_factory=make_dicts
    return db

def query_db(query, args=(),one=False):
    #query database using sql query
    #if app.config["DEBUG"]:
    print(query,args)
    c=get_db().execute(query,args)
    results=c.fetchall()
    #if app.config["DEBUG"]:
    print(len(results),"results")
    c.close()
    return (results[0] if results else None) if one else results

@app.teardown_appcontext
def close_db(exception):
    #close the database when the application closes
    db=get_db()
    if db is not None:
        db.close()
"""

def query_dict(query, **args):
    #query database using sql query
    #if app.config["DEBUG"]:
    try:
        print(query,args)
        if len(args) > 0:
            results = db.execute(query, args)
        else:
            results = db.execute(query)
        if results:
            results = [ dict(row) for row in results ]
            #if app.config["DEBUG"]:
            print ( results )
    except:
        print ( "ERROR: Query failed!" )
        return None
    return results

@app.route("/setup")
def setup():
    """ Creates the starting database"""
    password=generate_password_hash("password")
    #query=f"insert into login('username','password') values('admin','{password}')"
    #results=query_db(query,one=True)
    # results=db.engine.execute(query)# attempting SQL Alchemy 03/24/21

    # Clear all tables
    try:
        query = "delete from login where true;"
        db.execute(query)
        query = "delete from account where true;"
        db.execute(query)
    except:
        flash('Unable to clear existing database data.', 'danger')
        return redirect("/")

    try:
        query = "insert into login(username, password) values('admin',:password);"
        db.execute(query, password=password)
        query = "select userID from login where username='admin'"
        results = query_dict(query)
        query = "insert into account(userid, name, email) values(:userid, 'Admin', 'admin@mypantryy.com');"
        db.execute(query, userid=results[0]["userID"])
    except:
        flash('Unable to create starting database data.', 'danger')
        return redirect("/")
    flash('Database has been reset', 'success')
    return redirect("/")

@app.route('/')
def index():
    print(session)
    return render_template("index.html",session=session)

@app.route('/contact')
def contact():
    print(session)
    return render_template("contact.html",session=session)

@app.route('/myaccount')
def myaccount():
    print(session)
    return render_template("myaccount.html",session=session)

@app.route('/mymeds')
def mymeds():
    print(session)
    return render_template("mymeds.html",session=session)
@app.route('/mysub')
def mysub():
    print(session)
    return render_template("mysub.html",session=session)

@app.route('/mytask')
def mytask():
    print(session)
    return render_template("mytask.html",session=session)
@app.route('/mypantry')
def mypantry():
    print(session)
    return render_template("mypantry.html",session=session)

@app.route('/current')
def current():
    print(session)
    return render_template("current.html",session=session)

@app.route('/update')
def update():
    print(session)
    return render_template("update.html",session=session)

@app.route('/logout')
def logout():
    session.clear()
    print(session)
    return redirect('/')


@app.route('/login',methods=["GET","POST"])
def login():
    """Handles the login request.
       if a get request display login page.
       if a post request attempt to login a user"""
    if request.method=="GET":
        return render_template("login.html")
    elif request.method=="POST":
        username=""
        password=""
        if request.form.get("username"):
            username=request.form.get("username")
        if request.form.get("password"):
            password=request.form.get("password")
        # results=db.engine.execute(query) # attempting SQL Alchemy 03/24/21
        #query=f"select * from login where username='{username}';"
        #results=query_db(query,one=True)
        query = "select * from login where username=:username;"
        results = query_dict(query, username=username)
        if results is not None and len(results)>0 and check_password_hash(results[0]["password"],password):
            session["userID"]=results[0]["userID"]
            session["username"]=results[0]["username"]
            query="select name, email from account where userid=:userid"
            results=query_dict(query,userid=results[0]["userID"])
            if len(results)>0:
                session["name"]=results[0]["name"]
                session["email"]=results[0]["email"]
            flash('Congrats! You are logged in.', 'success')
            return redirect("/")
        else:
            flash('Invalid username or password!', 'danger')
            return render_template("login.html")

@app.route('/register',methods=["GET","POST"])
def register():
    """Handles the register request.
       if a get request display register page.
       if a post request attempt to register a user"""
    if request.method=="GET":
        return render_template("register.html")
    elif request.method=="POST":
        username=""
        password=""
        confirm=""
        name=""
        email=""
        if request.form.get("username"):
            username=request.form.get("username")
        else:
            flash('Invalid or missing username', 'danger')
            return render_template("register.html")
        if request.form.get("password"):
            password=request.form.get("password")
        else:
            flash('Invalid or missing password', 'danger')
            return render_template("register.html")
        if request.form.get("confirm") and request.form.get("confirm")==password:
            confirm=request.form.get("confirm")
        else:
            flash('Invalid or missing confirmation password', 'danger')
            return render_template("register.html")
        if request.form.get("name"):
            name=request.form.get("name")
        else:
            flash('Invalid or missing name', 'danger')
            return render_template("register.html")
        if request.form.get("email"):
            email=request.form.get("email")
        else:
            flash('Invalid or missing email', 'danger')
            return render_template("register.html")
        hashpass=generate_password_hash(password)
        #query=f"insert into login ('username','password') values('{username}','{hashpass}');"
        #results=query_db(query,one=True)
        query = "insert into login ('username','password') values(:username, :hashpass);"
        try:
            db.execute(query, username=username, hashpass=hashpass)
            query = "select userID from login where username=:username"
        except:
            flash('Username already taken', 'danger')
            return render_template("register.html")
        try:
            results = query_dict(query, username=username)
            query = "insert into account(userid, name, email) values(:userid, :name, :email);"
            db.execute(query, userid=results[0]["userID"], name=name, email=email)
        except:
            flash('Unexpected database error', 'danger')
            return render_template("register.html")

        flash('Registration complete! Please login with your new credentials.', 'success')
        return redirect("login")

@app.route('/search',methods=["GET","POST"])
def search():
    product=list(request.form["product"].lower())
    name="%".join(product)
    name="%"+name+"%"
    category=int(request.form["category"])
    is_custom="custom" in request.form
    if is_custom:
        if category>0:
            query = "select * from custom_products where user_id=:user_id and cat_id=:category and name like :name;"
            results = query_dict(query, user_id=session["userID"],category=category,name=name)
        else:
            query = "select * from custom_products where user_id=:user_id and name like :name;"
            results = query_dict(query, user_id=session["userID"],name=name)
    else:
        if category>0:
            query = "select * from product where cat_id=:category and name like :name;"
            results = query_dict(query, category=category,name=name)
        else:
            query = "select * from product where name like :name;"
            results = query_dict(query, name=name)
    return jsonify(results)
