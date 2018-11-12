# spellcheckweb
Application Security Web for Spell Check

Need to install

    flask

    python 3.7
  
    pyspellchecker ----- libary for spellcheck

Should install

    flask-WTF ------ communicate with html form and make forms easier to create in general
	
	flaskext-mysql ----- actually allow the Python script to manipulate databases

    passlib ------ specifically using sha 256 encryption, built in salts with that function and a verification function

	mysql-connector ------- connect to the MySQL database
	
	
	MySQL Database - name should be "users" with table "userpass". Current fields are "user" and "pass"
	
	

Tackling Security 

	- Some libraries in use come with input sanitization automatically applied, specifically stuff like flask
	- Use of csrf tokens in the forms to help prevent CSRF-based execution of them
	- Prepared statements considered, though potentially found unneeded due to input sanitization?