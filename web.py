from flask import Flask, render_template, flash, redirect, url_for, session, logging,request
#import MySQL???????
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from spellchecker import SpellChecker




app = Flask(__name__)

@app.route("/",methods=['GET','POST'])
def login():
    if(request.method=='POST'):
        username = request.form['username']
        password = request.form['password']

        #tempary user name and password, once a database is connnected, it will be use to compare to the database
        if (username == "root" and password == "toor"):
            return  redirect(url_for('spellcheck'))
    return render_template('login.html')


class RegisterForm(Form):
    username = StringField('Username', [validators.length(min=4, max=20)])
    password = PasswordField('Password',[
        validators.DataRequired(),
    ])

@app.route("/register", methods=['GET','POST'])
def register():
    #not very sure how to connect the user's input into the form
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))


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
