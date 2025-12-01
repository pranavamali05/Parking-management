from flask import Flask, request, render_template, redirect, flash
import mysql.connector
from mysql.connector import IntegrityError
import os
import mysql.connector

app = Flask(__name__)
app.secret_key = 'any_random_secret_key'

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME"),
    port=os.getenv("DB_PORT")
)


MAX_SLOTS = 100  


@app.route('/')
def index():
    search = request.args.get('search')
    cursor = db.cursor(dictionary=True)

    if search:
        cursor.execute("SELECT * FROM users WHERE vehiclenumber LIKE %s", (f"%{search}%",))
    else:
        cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT COUNT(vehiclenumber) AS total FROM users")
    total = cursor.fetchone()['total']


    cursor.execute("SELECT COUNT(vehiclenumber) AS total2 FROM users WHERE number_of_wheels = 2")
    total2 = cursor.fetchone()['total2']

    cursor.execute("SELECT COUNT(vehiclenumber) AS total4 FROM users WHERE number_of_wheels = 4")
    total4 = cursor.fetchone()['total4']


    remaining = MAX_SLOTS - total

    cursor.close()


    return render_template(
        "index.html",
        users=users,
        total=total,
        total2=total2,
        total4=total4,
        remaining=remaining,
        search=search
    )


@app.route('/add', methods=['POST'])
def add_user():
    firstname = request.form['firstname']
    middlename = request.form['middlename']
    lastname = request.form['lastname']
    vehiclenumber = request.form['vehiclenumber']
    number_of_wheels = request.form['number_of_wheels']
    ignition_type = request.form['ignition_type']
    mobile = request.form['mobile']
    address = request.form['address']

    cursor = db.cursor()
    cursor.execute("SELECT COUNT(vehiclenumber) FROM users")
    current_count = cursor.fetchone()[0]


    if current_count >= MAX_SLOTS:
        cursor.close()
        flash("Parking Full")
        return redirect('/')

    try:
        cursor.execute(
            "INSERT INTO users (firstname, middlename, lastname, vehiclenumber, number_of_wheels, ignition_type, mobile, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (firstname, middlename, lastname, vehiclenumber, number_of_wheels, ignition_type, mobile, address)
        )
        db.commit()
        flash("Vehicle added successfully")
    except IntegrityError:
        flash("Vehicle number already exists")
    finally:
        cursor.close()

    return redirect('/')


@app.route('/delete/<vehiclenumber>')
def delete_user(vehiclenumber):
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE vehiclenumber = %s", (vehiclenumber,))
    db.commit()
    cursor.close()
    flash("Vehicle entry deleted.")
    return redirect('/')


@app.route('/update/<vehiclenumber>', methods=['POST'])
def update_user(vehiclenumber):
    firstname = request.form['firstname']
    middlename = request.form['middlename']
    lastname = request.form['lastname']
    number_of_wheels = request.form['number_of_wheels']
    ignition_type = request.form['ignition_type']
    mobile = request.form['mobile']
    address = request.form['address']

    cursor = db.cursor()
    cursor.execute(
        "UPDATE users SET firstname=%s, middlename=%s, lastname=%s, number_of_wheels=%s, ignition_type=%s, mobile=%s, address=%s WHERE vehiclenumber=%s",
        (firstname, middlename, lastname, number_of_wheels, ignition_type, mobile, address, vehiclenumber)
    )
    db.commit()
    cursor.close()
    flash("Vehicle details updated.")
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
