from flask import g,Flask, redirect, render_template, request,session
#from flask_sqlalchemy import SQLAlchemy# attempting SQL Alchemy 03/24/21
import sqlite3
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
DATABASE=os.path.join(THIS_PATH, "data/my_pantry.db")
#db=SQLAlchemy.create_engine("sqlite:///"+DATABASE)# attempting SQL Alchemy 03/24/21
#app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///"+DATABASE
#db=SQLAlchemy(app)

def make_dicts(cur,row):
    """ convert the results of the query to a python dictionary"""
    return dict((cur.description[idx][0],value) for idx,value in enumerate(row))

def get_db():
    """function to retrieve the active Database"""
    db=getattr(g,"_database",None)
    if db==None:
        db=g._database=sqlite3.connect(DATABASE)
        db.row_factory=make_dicts
    return db

def query_db(query, args=(),one=False):
    """query database using sql query"""
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
    """close the database when the application closes"""
    db=get_db()
    if db is not None:
        db.close()


@app.route("/setup")
def setup():
    """ Creates the starting database"""
    password=generate_password_hash("password")
    query=f"insert into login('username','password') values('admin','{password}')"
    results=query_db(query,one=True)

    #results=db.engine.execute(query)# attempting SQL Alchemy 03/24/21
    print(results)
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
        query=f"select * from login where username='{username}';"
        #results=db.engine.execute(query) # attempting SQL Alchemy 03/24/21
        results=query_db(query,one=True)
        if results and check_password_hash(results["password"],password):
            session["userID"]=results["userID"]
            session["username"]=results["username"]
            return redirect("/")
        else:
            return render_template("login.html",alert_warning="Invalid username or password!")

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
            return render_template("register.html",alert_warning="Invalid or missing username")
        if request.form.get("password"):
            password=request.form.get("password")
        else:
            return render_template("register.html",alert_warning="Invalid or missing password")
        if request.form.get("confirm") and request.form.get("confirm")==password:
            confirm=request.form.get("confirm")
        else:
            return render_template("register.html",alert_warning="Invalid or missing confirmation password")
        if request.form.get("name"):
            name=request.form.get("name")
        else:
            return render_template("register.html",alert_warning="Invalid or missing name")
        if request.form.get("email"):
            email=request.form.get("email")
        else:
            return render_template("register.html",alert_warning="Invalid or missing email")
        hashpass=generate_password_hash(password)
        query=f"insert into login ('username','password') values('{username}','{hashpass}');"
        results=query_db(query,one=True)
        print(results)
        if results:
            userid=1
            query=f"insert into account ('userid','name','email') values('{userid}','{name}','{email}');"
            results=query_db(query,one=True)
            if results:
                return redirect("/login")
            else:
                return render_template("register.html",alert_warning="database error")
        else:
            return render_template("register.html",alert_warning="Username already taken")

