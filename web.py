from flask import Flask, render_template, flash, redirect, url_for, session, logging,request

from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from spellchecker import SpellChecker

#Okay yeah I have absolutely no idea what the hell any of this is anymore
#from MySQLdb import escape_string as thwart

#import mysql's connector to get that functionality
import mysql.connector




app = Flask(__name__)

@app.route("/",methods=['GET','POST'])
def login():
    if(request.method=='POST'):
        username = request.form['username']
        password = request.form['password']

        #for now just work with the established
        #local admin account for the SQL server
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                  #This is just a test password right now for the admin account
                  #obviously should be stronger
                user=username,
                passwd=password
            )

            return  redirect(url_for('spellcheck'))

        #password doesn't exist, send to register
        except:                    
            return  redirect(url_for('register'))
            
    return render_template('login.html')

#Registration form for new user
class RegisterForm(Form):
    username = StringField('Username', [validators.length(min=4, max=20)])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    
@app.route("/register", methods=['GET','POST'])
def register():
    #not very sure how to connect the user's input into the form
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

##        c, conn = connection()
##
##        x = c.execute("SELECT * FROM users WHERE username = (%s)",
##                      (thwart(username)))
##
##        if int(x) > 0:
##            flash("That username is already taken, choose another")
##
##        else:
##            c.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
##                      (thwart(username), thwart(password)))
##
##            conn.commit()
##            flash("Thanks for registering")
##            c.close()
##            conn.close()
                      

    #not sure how to add the username and password into a database,   please figure it out
    #I was thinking using mysql, but not sure how to do it
    #something like:
    #   mysql = mysql.connect()
    #   mysql.execute("INSERT INTO tableName(username, password) VALUES(%s,%s)",(username,passowrd))
    #   mysql.close()

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
