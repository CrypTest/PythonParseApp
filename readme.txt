====README====

This is a simple version of JSON-parser on Python.

Supported JSON-scheme:
https://s3.amazonaws.com/bluebite-backend-assignment/schema.json

Example of JSON-file:
https://s3.amazonaws.com/bluebite-backend-assignment/7447156584c543658455558747c64d2c.json

Dependencies:
- Python 3.6;
- Flask;
- Mysql.

Additional libraries for Python:
- mysql-connector-c.

The easiest way is to install Anaconda with Flask, Mysql and mysql-connector-c.

MySQL is chosen for this project, ‘cause Amazon databases support its SQL-syntax and entities.


====INSTALLATION====

Step 1. First one needs to install Python 3.6 with all dependencies.

Step 2. Copying index.py into the web-directory (some new folder).

Step 3. Changing MySQL Server parameters in the index.py file:
- C_DB_USER for MySQL username;
- C_DB_PASS for MySQL password;
- C_DB_HOST for MySQL host;

The project will create database and tables for itself. That’s why there’s no special need to change C_DB_NAME constant value.

Password for MySQL user can be changed with the following instructions:
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED BY 'mypass';

Step 4. Changing current directory to the www-root that contains the index.py file.

Step 5. Starting Flask:
FLASK_APP=index.py flask run.

By default, the project will become available in your browser by the following URL: http://127.0.0.1:5000/.

Step 6. Open the http://127.0.0.1/preinstall/ path to preinstall database of the project and tables.

Step 7. Use the http://127.0.0.1/ path to import JSON-files by their URLs.


====PATHS====

The project has the following root paths:
- "/" - for inputing URL to JSON-file and importing it;
- "/preinstall/" - to create a database and tables for the project.
- "/select" - for selecting all pairs (key, value) from the database by provider key;


===DATABASE STRUCTURE====

The project database consists of 2 tables.

Table t_keys (id, name) - contains keys.

Table t_keys_values (vendor varchar(50), tag varchar(50), key_id int, value varchar(50)) - contains keys and their values.

What is the t_keys table for?

This table contains all distinct keys to save database memory and make it work faster.
Due to that, we don't need to keep keys themselves into the t_keys_values table.

Why aren't vendors saved in a separate table the same way as keys?
That should be done, but was missed 'cause of time limit for the 1st phase of this project.


====WHAT WAS MISSED IN THIS VERSION. NEXT IMPROVEMENTS====

I. The script doesn't check whether JSON-file corresponds the general scheme;
II. Some errors should be processed with HTTP;
III. Database should be improved like described upon.






