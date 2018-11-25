#General Notes:
## input should be sanitized according to both Flask and mysql-connector
## 



from flask import Flask, render_template, flash, redirect, url_for, session, logging,request
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, logout_user
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from werkzeug import secure_filename
import logging
import os

#Okay, maybe import this instead for SQL stuff
from flaskext.mysql import MySQL

from passlib.hash import sha256_crypt
from spellchecker import SpellChecker
from logging import ERROR

#import mysql's connector to get that functionality
import mysql.connector

#Specify upload folder for files
UPLOAD_FOLDER = './checked_files/'


#Setup flask
app = Flask(__name__)
logger = logging.getLogger(__name__)

#Set up Info Handler
file_handler = logging.FileHandler('InfoLog.txt')
logging.basicConfig(filename='InfoLog.txt',level=logging.INFO)

#Set up Error Handler
file_handlerE = logging.FileHandler('ErrorLog.txt')
file_handlerE.setLevel(ERROR)

logger.addHandler(file_handlerE)




#login manager to help with sessions
login = LoginManager(app)



mysql = MySQL()

#Configuration stuff for the app
    #The account on the database is currently the root-like but not exactly root
    #test account
app.config['MYSQL_DATABASE_USER'] = 'test'
app.config['MYSQL_DATABASE_PASSWORD'] = 'test'
app.config['MYSQL_DATABASE_DB'] = 'users'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        self.id = int(i)
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
def load_user(uid):

    cursor = conn.cursor()
    ##get whatever's associated with the id
    cursor.execute('''SELECT * FROM userpass WHERE id = %s''', [uid])

                
                
    ##Check each item that matches (Probably just one now but just to be safe)
    storeduser = cursor.fetchone()

    
    #Return a user object
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
                #Username, hashed password, the id?
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
                logger.error('User: "' + username + '" failed to login')
                return  render_template('login.html', form=form, message="Invalid Username or Password")

            
            
        #In the case of some error, just redirect back to the login page for now
        except:
            cursor.close()
            logger.error('Unknown Error Occour')
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
            logger.error('New User: "' + username + '" failed to register')
            return render_template('register.html', form=form, message="The username is taken")
            
            

    
    cursor.close()
    return render_template('register.html', form=form, message="")


@app.route("/spellcheck", methods=['GET','POST'])
def spellcheck():

    ##WHY WON'T THIS WORK DAMN IT
    ##if not load_user(session['name']).is_authenticated:

    if not (session.get('logged_in')) == True:
        return redirect(url_for('login'))
    
    if (request.method == 'POST'):
        spell = SpellChecker()


        try:
            file = request.files['wrongText']
        except:
            file = None

        #If file exists, go through spellcheck
        if (file):

            #No blank file names
            if file.filename == '':
                return redirect(url_for('spellcheck'))
            
            #Sanitize file name input
            filename = secure_filename(file.filename)



            



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

                
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


            #Report size of file as seen in storage to log
            filesize = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], filename)).st_size
            logger.info('USER IS CHECKING: "' + filename + '" SIZE: ' + str(filesize) + ' AND FOUND ' + str(len(mispelled)) + ' ERRORS')
            
            return render_template('spellcheck.html', webresult=result)

        #Otherwise, go back to normal spellcheck
        else:
            return render_template('spellcheck.html')
        
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
