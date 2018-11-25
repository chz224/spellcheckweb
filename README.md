# spellcheckweb
Application Security Web for Spell Check

Need to install

    install flask
	install python 3.7
	install flask-WTF
	install passlib
	install pyspellchecker

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
	- Filenames given the "secure_filename" sanitization to prevent attacks on that nature hopefully
	
	
	
Issues still:
- Cannot spellcheck based on context still
- Cheng can't seem to get this running on his laptop, and it also seems like he's unable to plain test it at all some times of the day
