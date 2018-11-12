#General Notes:
## input should be sanitized according to both Flask and mysql-connector
## 



from flask import Flask, render_template, flash, redirect, url_for, session, logging,request
from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from werkzeug import secure_filename

#Okay, maybe import this instead for SQL stuff
from flaskext.mysql import MySQL


from passlib.hash import sha256_crypt
from spellchecker import SpellChecker


#import mysql's connector to get that functionality
import mysql.connector




app = Flask(__name__)
#app.secret_key = b'aaanwaf 3/1  3g]Anaa'


mysql = MySQL()

#Configuration stuff for the app
    #The account on the database is currently the root-like but not exactly root
    #test account
app.config['MYSQL_DATABASE_USER'] = 'test'
app.config['MYSQL_DATABASE_PASSWORD'] = 'test'
app.config['MYSQL_DATABASE_DB'] = 'users'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

app.config['SECRET_KEY'] = 'BolognaBoys'


mysql.init_app(app)

conn = mysql.connect()


@app.route("/",methods=['GET','POST'])
def login():
    cursor = conn.cursor()

    form = LoginForm(request.form)


    if(request.method=='POST'):
        username = form.username.data
        password = form.password.data


        try:
            ##get the hashed password corresponding to the username entered
            cursor.execute('''SELECT pass FROM userpass WHERE user = %s''', username)
            
            row = cursor.fetchone()
            ##Check each item that matches (Probably just one now but just to be safe)


            ##If the password is verified to the stored hash, "log in"
            if ((sha256_crypt.verify(password, row[0]))):
                print("FOUND, LOG IN")
                cursor.close()
                return  redirect(url_for('spellcheck'))
                
                
            
            
            print("NOT FOUND, GO BACK TO LOGIN")
            cursor.close()
            return redirect(url_for('login'))

            
            
        #In the case of some error, just redirect back to the login page for now
        except:
            print("ERROR, GO BACK TO LOGIN")
            cursor.close()
            return  redirect(url_for('login'))
    


        
            
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
    
    #not very sure how to connect the user's input into the form
    form = RegisterForm(request.form)

    
    
    if request.method=='POST':
        
        username = form.username.data
        password = form.password.data
        hashed = sha256_crypt.hash(password)
        
        
        try:
            cursor.execute('''INSERT INTO userpass(user,pass) VALUES (%s,%s)''',(username,hashed))
            conn.commit()
            cursor.close()
            return redirect(url_for('login'))

        #If either this doesn't work
        #Or the username already exists in the database, go back to register
        except:
            cursor.close()
            return  redirect(url_for('register'))
            
            

    print("RENDERING REGISTER");
    cursor.close()
    return render_template('register.html', form=form)


@app.route("/spellcheck", methods=['GET','POST'])
def spellcheck():
    if (request.method == 'POST'):
        spell = SpellChecker()


        try:
            file = request.files['wrongText']
        except:
            file = None

        if (file):
            filename = secure_filename(file.filename)




            result = " "

            #Read the file, split into words, decode from bytes to string
            words = file.read()
            words = words.decode("utf-8")
            words = words.split()
            
    
             

            mispelled = spell.unknown(words)
            print(mispelled)
            if (len(mispelled) > 0):
                for w in mispelled:
                    result = result + ", " + w
            else:
                result = "No Typos here!"
                
            return "The following are typos in the document: " + result
        else:
            return redirect(url_for('spellcheck'))
        
    return render_template('spellcheck.html')



if __name__ == "__main__":
    app.run(debug=True, port=5000)
