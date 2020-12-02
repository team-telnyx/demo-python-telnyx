import pymysql
import config

# Inserts a user into the database specified in config using MySQL
def InsertUser(new_user):
    # Connect to database
    try:
        connection = pymysql.connect(
            host=config.server_name, user=config.username, passwd=config.password, database=config.db
        )
    except:
        print("Failed to connect to", config.server_name, "( table:", config.db, ")")
        return False
    
    # Create connection cursor to execute query
    cursor = connection.cursor()
    query = f'INSERT INTO `users`(`username`, `password`, `phone`, `verified`) VALUES (\"{new_user.username}\", \"{new_user.password}\", \"{new_user.phone_number}\", 0)'
    cursor.execute(query)
    
    # Commit insert and close connection
    connection.commit()
    connection.close()
    return True

# Verifies a user in the database specified in config using MySQL
def VerifyUser(user):
    # Connect to database
    try:
        connection = pymysql.connect(
            host=config.server_name, user=config.username, passwd=config.password, database=config.db
        )
    except:
        print("Failed to connect to", config.server_name, "( table:", config.db, ")")
        return False
    
    # Create connection cursor to execute update
    cursor = connection.cursor()
    query = f'UPDATE `users` SET `verified`=1 WHERE `username`=\"{user.username}\"'
    cursor.execute(query)
    
    # Commit update and close connection
    connection.commit()
    connection.close()
    return True