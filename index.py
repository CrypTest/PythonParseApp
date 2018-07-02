"""
Application: Python JSON-Parser
Github: https://github.com/CrypTest/PythonParse
Author: Aslan Allakhkuliev
Created: 02/02/2018
"""

from flask import Flask
import json
import urllib3
import mysql.connector
from mysql.connector import errorcode
from flask import request

app = Flask(__name__)
C_DB_USER = "root"
C_DB_HOST = "127.0.0.1"
C_DB_PASS = "mypass"
C_DB_NAME = "mydb"

@app.route("/preinstall/")
def preinstall():
    try:
        cnn = mysql.connector.connect(user=C_DB_USER, password=C_DB_PASS, host=C_DB_HOST)
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return "Bad username or password"
        else:
            return e
    
    cursor = cnn.cursor()

    cmd = "CREATE DATABASE IF NOT EXISTS " + C_DB_NAME
    cursor.execute(cmd)

    cmd = "CREATE TABLE IF NOT EXISTS " + C_DB_NAME + ".t_keys ( ID int NOT NULL AUTO_INCREMENT, name varchar(20), PRIMARY KEY (ID) );"
    cursor.execute(cmd)

    cmd = "CREATE TABLE IF NOT EXISTS " + C_DB_NAME + ".t_keys_values ( vendor varchar(50), tag varchar(50), key_id int, value varchar(50) )"
    cursor.execute(cmd)

    return "Preinstall completed"


@app.route("/select/", methods=['GET'])
def select_form():
    
    output="<h3>Python JSON Parser - Select Keys & Values</h3>"

    output += "<form id='mainform' action='' method='post'>"
    output += "<input type='text' name='provider_key' value='' placeholder='Enter provider key here'/> "
    output += "<input type='button' value='Submit' onclick='document.getElementById(\"mainform\").submit();'/>"
    output += "</form>"
    return output


@app.route("/select/", methods=['POST'])
def select_process():

    output="<h3>Python JSON Parser - Select Keys & Values</h3>"

    try:
        cnn = mysql.connector.connect(user=C_DB_USER, password=C_DB_PASS, host=C_DB_HOST, database=C_DB_NAME)
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return "Bad username or password"
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            return "Database doesn't exist! <a href='/preinstall/'>Open the /preinstall/ url first!</a>"
        else:
            return e

    cursor = cnn.cursor()

    query_keys_values =  "SELECT k.name, f.value "
    query_keys_values += " FROM " + C_DB_NAME + ".t_keys_values as f"
    query_keys_values += " JOIN " + C_DB_NAME + ".t_keys as k ON f.key_id = k.id"
    query_keys_values += " WHERE f.vendor = '" + request.form["provider_key"] + "';"
    print(query_keys_values)    
    cursor.execute(query_keys_values)  

    result = []
    for (key_name, key_value) in cursor:
        d = {'key': key_name, 'value': key_value}
        result.append(d)
    
    print(result)
    cnn.close()

    output += "<br/><br/>Result:<br/><br/>"
    output += json.dumps(result)


    return output


@app.route('/', methods=['POST'])
def parse_request():
    output="<h3>Python JSON Parser - Import</h3>"
    try:
        cnn = mysql.connector.connect(user=C_DB_USER, password=C_DB_PASS, host=C_DB_HOST, database=C_DB_NAME)
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return "Bad username or password"
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            return "Database doesn't exist! <a href='/preinstall/'>Open the /preinstall/ url first!</a>"
        else:
            return e

    cursor = cnn.cursor()

    http = urllib3.PoolManager()
    url = request.form["path"]
    # Example: url = 'https://s3.amazonaws.com/bluebite-backend-assignment/a3e3853750724e2994515bb70d646c32.json'
    response = http.request('GET', url)
    data = json.loads(response.data)

    # Getting existing keys from database
    db_keys_names = []
    db_keys_ids = []

    query_keys = ("SELECT name, id FROM " + C_DB_NAME + ".t_keys ")       
    cursor.execute(query_keys)  

    for (key_name, key_id) in cursor:
        db_keys_names.append(key_name)
        db_keys_ids.append(key_id)

    # Listing keys and values from the json-file
    all_keys_names = []
    all_keys_tags = []
    all_values = []

    vendor_id = data['vendor_id']

    for t in data['tags']:
        #output += '<b>'+t['tag_id']+'</b><br/>'
        for kv in t['metadata']:
            #output += kv['key']+':'+kv['value']+'<br/>'
            all_keys_names.append(kv['key'])
            all_values.append(kv['value'])
            all_keys_tags.append(t['tag_id'])
    
    print(db_keys_names)
    # Looking for new keys and adding them to the database, getting their ids
    distinct_all_keys_names = list(set(all_keys_names))
    for key_name in distinct_all_keys_names:
        if (key_name not in db_keys_names):
            db_keys_names.append(key_name)
            query_insert_new_key = "INSERT INTO " + C_DB_NAME + ".t_keys (name) VALUES ('" + key_name + "');"
            cursor.execute(query_insert_new_key)
            cnn.commit()
            db_keys_ids.append(cursor.lastrowid)

    # Inserting values into database
    for key_tag, keys_name, key_value in zip(all_keys_tags, all_keys_names, all_values):
        key_id = str(db_keys_ids[db_keys_names.index(keys_name)])
        query_insert_new_value = "INSERT INTO " + C_DB_NAME + ".t_keys_values (vendor, tag, key_id, value) VALUES ('" + vendor_id + "', '" + key_tag + "', " + key_id + ", '" + key_value + "')"
        cursor.execute(query_insert_new_value)
        cnn.commit()
    
    cnn.close()
    
    output += "<br/><b>Success!</b><br/><br/>"
    output += "Vendor code: <b>" + vendor_id + "</b><br/><br/><b>Use it for <a href='/select/'>selecting values from database</a>.</b><br/>"

    return output


@app.route("/")
def index():

    output="<h3>Python JSON Parser - Import</h3>"
    output += "<form id='mainform' action='/' method='post'>"
    output += "<input type='text' name='path' value='' placeholder='Enter the path to JSON here'/> "
    output += "<input type='button' value='Submit' onclick='document.getElementById(\"mainform\").submit();'/>"
    output += "</form>"
    return output


if __name__ == '__main__':
    app.run(debug=True)