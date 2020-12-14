import pymysql
import config
import os

def InitiateConnection():
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_SERVER_NAME"), user=os.getenv("DB_USERNAME"), passwd=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME")
        )
    except:
        print("Failed to connect to", os.getenv("DB_SERVER_NAME"), "( table:", os.getenv("DB_NAME"), ")", flush=True)
        return None

    return connection

# Inserts a user into the database specified in config using MySQL
def InsertUser(new_user):
    # Connect to database
    connection = InitiateConnection()
    
    try:
        # Create connection cursor to execute query
        cursor = connection.cursor()
        query = f'INSERT INTO `users`(`username`, `password`, `phone`, `verified`) VALUES (%s, %s, %s, 0)'
        cursor.execute(query, (new_user.username, new_user.password, new_user.phone_number))

        # Commit insert and close connection
        connection.commit()
        connection.close()
        return True
    except:
        print("Failed to insert new user to database")
        return False

# Verifies a user in the database specified in config using MySQL
def VerifyUser(username):
    # Connect to database
    connection = InitiateConnection()
    
    try:
        # Create connection cursor to execute update
        cursor = connection.cursor()
        query = f'UPDATE `users` SET `verified`=1 WHERE `username`=%s'
        cursor.execute(query, (username))
        
        # Commit update and close connection
        connection.commit()
        connection.close()
        return True
    except:
        print("Failed to verify user")
        return False

# Checks that a username and password combination are correct
def LoginUser(user):
    # Connect to database
    connection = InitiateConnection()

    try:
        # Create connection cursor to execute search for user
        cursor = connection.cursor()
        query = f'SELECT * FROM `users` WHERE `username`=%s'
        cursor.execute(query, (user.username))

        result = cursor.fetchall()

        connection.close()

        # If no one has this username
        if not result:
            return False

        # If the password matches the inputted password
        if result[0][1] == user.password:
            return True
        
        return False
    except:
        print("Failed to log in user")
        return False

# Checks if a username is already in use
def CheckUsername(user):
    # Connect to database
    connection = InitiateConnection()
    
    try:
        # Create connection cursor to execute check for user
        cursor = connection.cursor()
        query = f'SELECT * FROM `users` WHERE `username`=%s'
        cursor.execute(query, (user.username))

        result = cursor.fetchall()

        connection.close()

        # If we found a match for this username, return False
        if result:
            return False
        return True
    except:
        print("Failed to check username")
        return False