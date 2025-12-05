from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3

app = Flask(__name__)

# ------------------------------
# ENV VARS FROM CONFIGMAP/SECRET
# ------------------------------
DBHOST = os.getenv("DBHOST")
DBUSER = os.getenv("DBUSER")
DBPWD = os.getenv("DBPWD")
DATABASE = os.getenv("DATABASE")
DBPORT = int(os.getenv("DBPORT"))

APP_COLOR = os.getenv("APP_COLOR", "lime")
APP_AUTHOR = os.getenv("APP_AUTHOR", "Asaad")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY")            # e.g. bg.png

# DB connection
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

# ------------------------------
# DOWNLOAD BACKGROUND FROM S3
# ------------------------------
def download_background():
    if not S3_BUCKET or not S3_KEY:
        print("Missing S3_BUCKET or S3_KEY")
        return

    s3 = boto3.client("s3")
    local_path = f"/app/static/{S3_KEY}"

    try:
        s3.download_file(S3_BUCKET, S3_KEY, local_path)
        print(f"Downloaded background image to {local_path}")
    except Exception as e:
        print("Failed to download S3 image:", e)


# ------------------------------
# ROUTES
# ------------------------------
@app.route("/")
def home():
    download_background()
    return render_template(
        "addemp.html",
        color=APP_COLOR,
        author=APP_AUTHOR,
        bg_image=S3_KEY
    )

@app.route("/about")
def about():
    download_background()
    return render_template(
        "about.html",
        color=APP_COLOR,
        author=APP_AUTHOR,
        bg_image=S3_KEY
    )


# ------------------------------
# OTHER ROUTES (unchanged)
# ------------------------------
@app.route("/addemp", methods=['POST'])
def addemp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    cursor = db_conn.cursor()
    try:
        insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
    finally:
        cursor.close()

    full_name = f"{first_name} {last_name}"
    return render_template("addempoutput.html",
                           name=full_name,
                           color=APP_COLOR,
                           author=APP_AUTHOR)

@app.route("/getemp")
def getemp():
    return render_template("getemp.html",
                           color=APP_COLOR,
                           author=APP_AUTHOR)

@app.route("/fetchdata", methods=['POST'])
def fetchdata():
    emp_id = request.form['emp_id']
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s", (emp_id,))
        row = cursor.fetchone()
    finally:
        cursor.close()

    if not row:
        return f"No employee found with ID {emp_id}", 404

    return render_template(
        "getempoutput.html",
        id=row[0], fname=row[1], lname=row[2],
        interest=row[3], location=row[4],
        color=APP_COLOR,
        author=APP_AUTHOR
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)