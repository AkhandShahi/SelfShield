from bson import ObjectId
from flask import Flask, render_template, request, redirect, session
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import qrcode
import json
import os
from pyzbar.pyzbar import decode
import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/User"
mongo = PyMongo(app)
app.secret_key = 'akhand13shahi'
app.debug = True
app.static_folder = 'static'

@app.route('/')
def home():
    # check if user is logged in
    if 'user_id' in session:
        user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
        return render_template('index.html', user=user)
    else:
        return render_template('index.html')


@app.route('/portal')
def portal():
    if 'user_id' in session:
        user = mongo.db.partner.find_one({'_id': ObjectId(session['user_id'])})
        user_id = str(user['_id'])
        print(type(user_id))
        drivers = mongo.db.driver
        drivers = drivers.find({'Owner_id': user_id})
        names = []
        images = []
        phone = []
        vehicle =[]
        number = []
        driver_id = []
        qr = []

        for driver in drivers:
            x = driver['name']
            y = driver['image']
            z = driver['phone']
            i = driver['vehicle']
            j = driver['number']
            d_id = driver['_id']
            qr_code = driver['qr_code']

            driver_id.append(d_id)
            phone.append(z)
            names.append(x)
            images.append(y)
            vehicle.append(i)
            number.append(j)
            qr.append(qr_code)

        count = len(names)
        return render_template('portal.html', user=user, names=names, images=images, count=count,
                               phone=phone, vehicle=vehicle, number=number, driver_id=driver_id, qr = qr)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        email = request.form['email']
        password = request.form['password']

        errors = []

        existing_email = users.find_one({'email': email})

        # Authenticate user

        if existing_email:
            existing_user = users.find_one({'email': email, 'password': password})
            print(existing_user)
            if existing_user:
                print(existing_user)
                session['user_id'] = str(existing_user['_id'])
                #img_path = "{{url_for('static', filename='user_image/{}')}}".format(existing_user.image)
                return redirect('/')
            else:
                errors.append('Invalid password')
                return render_template('login.html', errors=errors)

        else:
            errors.append('Email not found in record. Create an account')
            return render_template('login.html', errors=errors)

    else:
        return render_template('login.html')

@app.route('/v_login', methods=['POST'])
def v_login():
    if request.method == 'POST':
        users = mongo.db.partner
        email = request.form['email']
        password = request.form['password']

        errors = []

        existing_email = users.find_one({'email': email})

        # Authenticate user

        if existing_email:
            existing_user = users.find_one({'email': email, 'password': password})
            print(existing_user)
            if existing_user:
                print(existing_user)
                session['user_id'] = str(existing_user['_id'])
                #img_path = "{{url_for('static', filename='user_image/{}')}}".format(existing_user.image)
               
                return redirect('portal')
            else:
                errors.append('Invalid password')
                return render_template('login.html', errors=errors)

        else:
            errors.append('Email not found in record. Create an account')
            return render_template('login.html', errors=errors)

    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['pwd1']
        confirm_pwd = request.form['pwd2']
        file = request.files['image']

        filename = secure_filename(file.filename)

        file.save(os.path.join('static/user_image', filename))

        errors = []

        if password == confirm_pwd:
            existing_user = users.find_one({'email': email})
            if existing_user:
                errors.append('User already created, change your email')
                return render_template('sign.html', errors=errors)
            else:
                user_id = users.insert_one({'name': name, 'email': email, 'phone': phone,
                                            'password': password, 'image': filename})
                print(user_id)
                info = ['Successfully created an account. Login Here']
                return render_template('login.html', info=info)

        else:
            errors.append('Passwords do not match')
            return render_template('sign.html', errors=errors)
    else:
        return render_template('sign.html')

@app.route('/v_register', methods=['POST'])
def v_register():
    if request.method == 'POST':
        users = mongo.db.partner
        name = request.form['v-name']
        email = request.form['v-email']
        phone = request.form['v-phone']
        password = request.form['pwd1']
        confirm_pwd = request.form['pwd2']
        file = request.files['v-image']

        filename = secure_filename(file.filename)

        file.save(os.path.join('static/partner_img', filename))

        errors = []

        if password == confirm_pwd:
            existing_user = users.find_one({'email': email})
            if existing_user:
                errors.append('User already created, change your email')
                return render_template('sign.html', errors=errors)
            else:
                user_id = users.insert_one({'name': name, 'email': email, 'phone': phone,
                                            'password': password, 'image': filename})
                print(user_id)
                info = ['Successfully created an account. Login Here']
                return render_template('login.html', info=info)

        else:
            errors.append('Passwords do not match')
            return render_template('sign.html', errors=errors)
    else:
        return render_template('sign.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/add_driver', methods=['POST'])
def add_driver():
    if request.method == 'POST':
        users = mongo.db.driver
        name = request.form['name']
        phone = request.form['phone']
        vehicle = request.form['vehicle']
        number = request.form['number']
        img = request.files['image']
        aadhar = request.files['aadhar']
        license = request.files['license']
        owner_id = request.form['id']

        data = {'name': name, 'phone': phone, 'vehicle': vehicle, 'number': number}
        data_string = json.dumps(data)
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(data_string)
        qr.make(fit=True)
        qr_code = qr.make_image(fill_color="black", back_color="white")
        qr_code_filename = '{}-qr.png'.format(name)

        filename1 = secure_filename(img.filename)
        filename2 = secure_filename(aadhar.filename)
        filename3 = secure_filename(license.filename)
        filename4 = secure_filename(qr_code_filename)

        img.save(os.path.join('static/driver_image', filename1))
        aadhar.save(os.path.join('static/driver_aadhar', filename2))
        license.save(os.path.join('static/driver_license', filename3))
        qr_code.save(os.path.join('static/driver_qr', filename4))

        users.insert_one({'Owner_id': owner_id, 'name': name, 'phone': phone, 'vehicle': vehicle, 'number': number,
                          'image': filename1, 'aadhar': filename2, 'license': filename3, 'qr_code':filename4})
        return redirect('portal')

@app.route('/delete_driver', methods=['POST'])
def delete_driver():
    if request.method == 'POST':
        d_id = request.form['d_id']
        mongo.db.driver.delete_one({'_id': ObjectId(d_id)})
        return redirect('portal')

def scan_qr_code():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        decoded_objects = pyzbar.decode(gray)

        cv2.imshow('QR Scanner', frame)

        if decoded_objects:
            qr_data = decoded_objects[0].data.decode('utf-8')
            return qr_data

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/scan')
def scan():
    qr_data = scan_qr_code()
    return qr_data


if __name__ == "__main__":
    app.run()
