#General Notes:
## input should be sanitized according to both Flask and mysql-connector
## 



from flask import Flask, render_template, flash, redirect, url_for, session, logging,request
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, logout_user
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from werkzeug import secure_filename
import logging

#Okay, maybe import this instead for SQL stuff
from flaskext.mysql import MySQL

from passlib.hash import sha256_crypt
from spellchecker import SpellChecker


#import mysql's connector to get that functionality
import mysql.connector

#Setup flask
app = Flask(__name__)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('ErrorLog.txt')
logging.basicConfig(filename='ErrorLog.txt',level=logging.INFO)

#login manager to help with sessions
login = LoginManager(app)



mysql = MySQL()

#Configuration stuff for the app
    #The account on the database is currently the root-like but not exactly root
    #test account
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'toor'
app.config['MYSQL_DATABASE_DB'] = 'users'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'

app.config['SECRET_KEY'] = 'BolognaBoys'


#Initialize the mysql and login with the app
mysql.init_app(app)
login.init_app(app)

#connect app to database
conn = mysql.connect()

#Make a user class of some sort
class User(UserMixin):
    def __init__(self, un, p, i):
        self.username = un;
        self.passhash = p;
        self.id = i
        self.active = True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.id

#Set user_loader callback
@login.user_loader
def load_user(id):
    cursor = conn.cursor()
    ##get whatever's associated with the user
    cursor.execute('''SELECT * FROM userpass WHERE id = %s''', id)
            
            
    ##Check each item that matches (Probably just one now but just to be safe)
    storeduser = cursor.fetchone()
    return User(storeduser[1], storeduser[2], storeduser[0])




@app.route("/",methods=['GET','POST'])
def login():
    cursor = conn.cursor()

    form = LoginForm(request.form)
    logger.info('Unknown user open the website')

    if(request.method=='POST'):
        username = form.username.data
        


        try:
            ##get the hashed password corresponding to the username entered
            cursor.execute('''SELECT * FROM userpass WHERE user = %s''', username)
            logger.info('User: "' + username + '" attempt to login')
                
                ##Check each item that matches (Probably just one now but just to be safe)
            storeduser = cursor.fetchone()

                ##If the password is verified to the stored hash, "log in"
            if (sha256_crypt.verify(form.password.data, storeduser[2])):


                    #Make a new user object to log in for now?
                user = User(username, storeduser[2], storeduser[0])

                login_user(user)
                    
                cursor.close()


                    

                    #I don't know, just make it so session is of the username
                session['name'] = username
                session['logged_in'] = True
                    

                app.logger.info('%s logged in successfully', username)
                logger.info('User: "' + username + '" successfully login')

                return  redirect(url_for('spellcheck'))

                    
            else:    
                cursor.close()
                abort(401)
                logger.info('User: "' + username + '" failed to login')
                return  render_template('login.html', form=form, message="Invalid Username or Password")

            
            
        #In the case of some error, just redirect back to the login page for now
        except:
            cursor.close()
            logger.info('Unknown Error Occour')
            return   render_template('login.html', form=form, message="Unknown Error: please try again")
    


        
            
    return render_template('login.html', form=form)

#Registration form for new user
class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.length(min=4, max=20)])
    password = PasswordField('Password',[
        validators.DataRequired()
        
    ])

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.length(min=4, max=20)])
    password = PasswordField('Password',[
        validators.DataRequired()
        
    ])
    
@app.route("/register", methods=['GET','POST'])
def register():

    cursor = conn.cursor()
    
    form = RegisterForm(request.form)

    
    
    if request.method=='POST':
        
        username = form.username.data
        password = form.password.data
        hashed = sha256_crypt.hash(password)
        logger.info('New User: "' + username + '"')
        
        
        try:
            cursor.execute('''INSERT INTO userpass(user,pass) VALUES (%s,%s)''',(username,hashed))
            conn.commit()
            cursor.close()
            logger.info('New User: "' + username + '" successfully registered')
            return redirect(url_for('login'))

        #If either this doesn't work
        #Or the username already exists in the database, go back to register
        except:
            cursor.close()
            logger.info('New User: "' + username + '" failed to register')
            return render_template('register.html', form=form, message="The username is taken")
            
            

    
    cursor.close()
    return render_template('register.html', form=form, message="")


@app.route("/spellcheck", methods=['GET','POST'])
def spellcheck():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if (request.method == 'POST'):
        spell = SpellChecker()


        try:
            file = request.files['wrongText']
        except:
            file = None

        if (file):
            filename = secure_filename(file.filename)
            logger.info('User spell checked: "' + filename + '"')




            result = " "

            #Read the file, split into words, decode from bytes to string
            words = file.read()
            words = words.decode("utf-8")
            words = words.split()
            
    
             

            mispelled = spell.unknown(words)
            if (len(mispelled) > 0):
                for w in mispelled:
                    result = result + ", " + w
            else:
                result = "No Typos here!"
                
            return render_template('spellcheck.html', webresult=result)
        else:
            return render_template('spellcheck.html', webresult="No Typos here")
        
    return render_template('spellcheck.html', webresult="None So Far!")

#Route for logouts
@app.route("/logout")
def logout():
    logger.info('User log out')
    logout_user()
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
