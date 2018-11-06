from flask import Flask, render_template, flash, redirect, url_for, session, logging,request

#Okay, maybe import this instead for SQL stuff
from flaskext.mysql import MySQL

from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from spellchecker import SpellChecker

#Okay yeah I have absolutely no idea what the hell any of this is anymore


#import mysql's connector to get that functionality
import mysql.connector




app = Flask(__name__)
#app.secret_key = b'aaanwaf 3/1  3g]Anaa'


mysql = MySQL()

#Configuration stuff for the app
    #The account on the database is currently the root-like but not exactly root
    #test account
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pass'
app.config['MYSQL_DATABASE_DB'] = 'users'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()


@app.route("/",methods=['GET','POST'])
def login():
    cursor = conn.cursor()

    if(request.method=='POST'):
        username = request.form['username']
        password = request.form['password']

        #Test out connection to current database
        cursor.execute('''SELECT user FROM userpass''')
        rv = cursor.fetchall()
        return str(rv)


    
        return  redirect(url_for('login'))
##        try:
##            cursor.execute("SELECT user FROM users.userpass WHERE (user=\"" + username "\" AND pass=\"" + password + "\");")
##            return  redirect(url_for('spellcheck'))
##        except:           
##            return  redirect(url_for('/'))
    


        
            
    return render_template('login.html')

#Registration form for new user
class RegisterForm(Form):
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
        password = sha256_crypt.hash(str(form.password.data))

        
        ##NEED TO CHECK PASSWORD HASH LENGTH, ADJUST PASSWORD FIELD IN DATABASE TO MATCH
        try:
            ##cursor.execute("INSERT INTO userpass(user, pass) VALUES (\"" + username + "\", \"" + password + "\")")
            cursor.execute('''INSERT INTO userpass(user,pass) VALUES (%s,%s)''',(username,password))
            conn.commit()
            print("FINALLY WORKED, GO TO LOGIN")
            return redirect(url_for('login'))
        except:
            print("OOPS, GOING TO REGISTER AGAIN")
            return  redirect(url_for('register'))
            
            

    print("RENDERING REGISTER");
    return render_template('register.html', form=form)


@app.route("/spellcheck", methods=['GET','POST'])
def spellcheck():
    if (request.method == 'POST'):
        spell = SpellChecker()
        misspelledTexts = request.form['wrongText']
        result = ""
        for word in misspelledTexts.split():
            result = result +" "+ str(spell.candidates(word))
        return result
    return render_template('spellcheck.html')



if __name__ == "__main__":
    app.run(debug=True, port=5000)
