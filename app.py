""""

from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse


app = Flask(__name__)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "Passw0rd"
DATABASE = os.environ.get("DATABASE") or "employees"
COLOR_FROM_ENV = os.environ.get('APP_COLOR') or "lime"
DBPORT = int(os.environ.get("DBPORT") or 3306)

# Create a connection to the MySQL database
#db_conn = connections.Connection(
#    host= DBHOST,
#    port=DBPORT,
#   user= DBUSER,
#   password= DBPWD, 
 #   db= DATABASE
#    
#)
#output = {}
#table = 'employee';

# Define the supported color codes
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}


# Create a string of supported colors
SUPPORTED_COLORS = ",".join(color_codes.keys())

# Generate a random color
COLOR = random.choice(["red", "green", "blue", "blue2", "darkblue", "pink", "lime"])


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', color=color_codes[COLOR])

@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html', color=color_codes[COLOR])
    
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

  
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        
        cursor.execute(insert_sql,(emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, color=color_codes[COLOR])

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", color=color_codes[COLOR])


@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()
        
        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
        
    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], color=color_codes[COLOR])

if __name__ == '__main__':
    
    # Check for Command Line Parameters for color
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        print("Color from command line argument =" + args.color)
        COLOR = args.color
        if COLOR_FROM_ENV:
            print("A color was set through environment variable -" + COLOR_FROM_ENV + ". However, color from command line argument takes precendence.")
    elif COLOR_FROM_ENV:
        print("No Command line argument. Color from environment variable =" + COLOR_FROM_ENV)
        COLOR = COLOR_FROM_ENV
    else:
        print("No command line argument or environment variable. Picking a Random Color =" + COLOR)

    # Check if input color is a supported one
    if COLOR not in color_codes:
        print("Color not supported. Received '" + COLOR + "' expected one of " + SUPPORTED_COLORS)
        exit(1)

    app.run(host='0.0.0.0',port=8080,debug=True)
"""

from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse
import boto3   # For S3 download

app = Flask(__name__)

# ----------------------------------------------------
# ENVIRONMENT VARIABLES (ConfigMap + Secrets in EKS)
# ----------------------------------------------------
DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "Passw0rd"
DATABASE = os.environ.get("DATABASE") or "employees"
DBPORT = int(os.environ.get("DBPORT") or 3306)

COLOR_FROM_ENV = os.environ.get('APP_COLOR') or "lime"
BACKGROUND_IMAGE_URL = os.environ.get("BACKGROUND_IMAGE_URL")
APP_AUTHOR = os.environ.get("APP_AUTHOR", "ABJ")

# ----------------------------------------------------
# DISABLE DATABASE CONNECTION LOCALLY (ENABLE IN EKS)
# ----------------------------------------------------
"""
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)
"""
#output = {}
#table = 'employee'

# ----------------------------------------------------
# COLOR SUPPORT
# ----------------------------------------------------
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}

SUPPORTED_COLORS = ",".join(color_codes.keys())
COLOR = random.choice(list(color_codes.keys()))

# ----------------------------------------------------
# BACKGROUND IMAGE DOWNLOAD FUNCTION
# ----------------------------------------------------
def download_background_image():
    if not BACKGROUND_IMAGE_URL:
        print("No BACKGROUND_IMAGE_URL provided. Using default background.")
        return

    print("Using background image URL:", BACKGROUND_IMAGE_URL)

    try:
        s3 = boto3.client("s3")

        # Parse the S3 bucket and key
        # Example: s3://mybucket/path/image.jpg
        cleaned_url = BACKGROUND_IMAGE_URL.replace("s3://", "")
        bucket = cleaned_url.split("/")[0]
        key = "/".join(cleaned_url.split("/")[1:])

        local_path = "static/background.jpg"

        s3.download_file(bucket, key, local_path)
        print("Downloaded background image to:", local_path)

    except Exception as e:
        print("Failed to download background image:", e)

# ----------------------------------------------------
# ROUTES
# ----------------------------------------------------
@app.route("/", methods=['GET', 'POST'])
def home():
    download_background_image()
    return render_template('addemp.html',
                           color=color_codes[COLOR],
                           author=APP_AUTHOR)

@app.route("/about", methods=['GET','POST'])
def about():
    download_background_image()
    return render_template('about.html',
                           color=color_codes[COLOR],
                           author=APP_AUTHOR)


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    # --------------------------------------
    # DISABLED LOCALLY — ENABLE IN EKS
    # --------------------------------------
    """
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql,(emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = first_name + " " + last_name
    finally:
        cursor.close()
    """

    emp_name = first_name + " " + last_name  # Temporary local behavior
    print("Simulated insert complete (DB disabled locally).")

    return render_template('addempoutput.html',
                           name=emp_name,
                           color=color_codes[COLOR],
                           author=APP_AUTHOR)


@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html",
                           color=color_codes[COLOR],
                           author=APP_AUTHOR)


@app.route("/fetchdata", methods=['POST'])
def FetchData():
    emp_id = request.form['emp_id']

    # --------------------------------------
    # DISABLED LOCALLY — ENABLE IN EKS
    # --------------------------------------
    """
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()
    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()

        output = {
            "emp_id": result[0],
            "first_name": result[1],
            "last_name": result[2],
            "primary_skills": result[3],
            "location": result[4]
        }
    finally:
        cursor.close()
    """

    # Placeholder results for local testing
    output = {
        "emp_id": emp_id,
        "first_name": "Test",
        "last_name": "User",
        "primary_skills": "None",
        "location": "Local"
    }

    return render_template("getempoutput.html",
                           id=output["emp_id"],
                           fname=output["first_name"],
                           lname=output["last_name"],
                           interest=output["primary_skills"],
                           location=output["location"],
                           color=color_codes[COLOR],
                           author=APP_AUTHOR)

# ----------------------------------------------------
# APP ENTRY POINT
# ----------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        print("Color from command line argument =", args.color)
        COLOR = args.color
    elif COLOR_FROM_ENV:
        print("Using color from environment variable =", COLOR_FROM_ENV)
        COLOR = COLOR_FROM_ENV
    else:
        print("No color provided. Using random color =", COLOR)

    if COLOR not in color_codes:
        print("Invalid color. Choose one of:", SUPPORTED_COLORS)
        exit(1)

    print("App Author:", APP_AUTHOR)
    print("Background Image URL:", BACKGROUND_IMAGE_URL)

    app.run(host='0.0.0.0', port=81, debug=True)
