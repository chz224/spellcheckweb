#This just tests the SQL Database and all that


import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  #This is just a test password right now for the admin account
  #obviously should be stronger
  user="test",
  passwd="test"
)

#create a cursor
mycursor = mydb.cursor()

#for now, just either add a database or remove the database that exists
try:
    mycursor.execute("CREATE DATABASE mydatabase")
    print("DATABASE MADE")
except:
    mycursor.execute("DROP DATABASE mydatabase")
    print("DATABASE REMOVED")


