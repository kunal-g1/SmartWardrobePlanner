from flask import Flask, render_template, request, redirect, session
import random
from cv2 import cv2
import  pandas as pd
import numpy as np 
import tensorflow as tf
# import tensorflow as tf
# from keras.preprocessing.image import load_img
# from keras.preprocessing.image import img_to_array
# from keras.models import load_model
from tensorflow.keras.models import load_model
import mysql.connector
import os

app=Flask(__name__)
app.config['UPLOAD_FOLDER'] ="C:\\Flask\\SmartWardrobePlanner\\wardrobe_users"
app.secret_key=os.urandom(24)

conn=mysql.connector.connect(host="localhost", user="root" ,password="", database="wardrobe_users")
cursor=conn.cursor()

classification_loaded_model = load_model('Clothes Classification/class_model.h5')
def classfiy_image(img):
    img=cv2.imread(img)
    img=cv2.GaussianBlur(img,(3,3),9)
    img=cv2.resize(img,(128,128),cv2.INTER_AREA)
    img=img/255
    x=[]
    x.append(img)
    x=np.asarray(x)
    prediction=classification_loaded_model.predict_classes(x,True,None)
    print(prediction[0])
    return prediction[0]

# app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
# ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
# def allowed_file(filename):
#     return '.' in filename and \
#         filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# def init():
#     global graph
    # graph = tf.get_default_graph()

@app.route('/')
def login_SignUp():
    return render_template('login_SignUp.html')

@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    return redirect('/')

@app.route('/your_closet', methods=['GET', 'POST'])
def your_closet():
    if request.method=='POST':
        # print(request.files)
        image=request.files['user_image']
        # os.mkdir('static')
        image.save(os.path.join('static/temp',image.filename))
        file_saved=os.path.join('static/temp',image.filename)
        
        class_prediction=classfiy_image(file_saved)
        if class_prediction==0:
            product="T-shirts"
        elif class_prediction==1:
            product="Shirts"
        elif class_prediction==2:
            product="Shorts"
        elif class_prediction==3:
            product="Pants"
        elif class_prediction==4:
            product="Jackets"
        # cursor.execute(""" SELECT * from `users` where `email` LIKE '{}'""".format(email))
        # myuser=cursor.fetchall()
        # session['user_id']=myuser[0][1]
        file_path=os.path.join('wardrobe_users/{}/{}'.format(session['user_id'],product),image.filename)
        image.save(file_path)
        print(class_prediction)
        # shirts=os.listdir('shirts')
        os.remove(file_saved)
        # image.save(ENTER FILE WHERE YOU WANT TO SAVE IMAGE)
    Tshirts=os.listdir('wardrobe_users/{}/T-shirts'.format(session['user_id']))
    print(Tshirts)
    Tshirts_new=[]
    Shirts=os.listdir('wardrobe_users/{}/Shirts'.format(session['user_id']))
    Shorts=os.listdir('wardrobe_users/{}/Shorts'.format(session['user_id']))
    Pants=os.listdir('wardrobe_users/{}/Pants'.format(session['user_id']))
    Jackets=os.listdir('wardrobe_users/{}/Jackets'.format(session['user_id']))
    user=session['user_id']
    print(user)
    for i in Tshirts:
        t='wardrobe_users\\kunalgoel@gmail.com\\T-shirts\\'+i
        Tshirts_new.append(t)
    print(Tshirts_new)

    return render_template('your_closet.html', Tshirts=Tshirts_new,  Shirts=Shirts, Shorts=Shorts, Pants=Pants, Jackets=Jackets, user=user)
 
    # global graph
    # if request.method == 'POST':
    #     file = request.files['file']
    #     try:
    #         if file and allowed_file(file.filename):
    #             filename=file.filename
    #             img = load_img(filename)

    #             with  graph.as_default():
    #                 model1=load_model('class_model.h5')
    #                 class_prediction = model1.predict_classes(img)

    #             if class_prediction[0]==0:
    #                 product="T-shirts"
    #             elif class_prediction[0]==1:
    #                 product="Shirts"
    #             elif class_prediction[0]==2:
    #                 product="Shorts"
    #             elif class_prediction[0]==3:
    #                 product="Pants"
    #             elif class_prediction[0]==4:
    #                 product="Jackets"
                
    #             file_path=os.path.join('static/wardrobe_users/{}/{}'.format('user_id',product))
    #             file.save(file_path)
    #     except Exception as e:
    #         return "Unable to read the file. Please Check if the file extension is correct."
                
    # if 'user_id' in session:
    #     return render_template('your_closet.html')
    # return redirect('/')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email=request.form.get('email')
    password=request.form.get('password')
    cursor.execute(""" SELECT * from `users` where `email` LIKE '{}' and `password` LIKE '{}'""".format(email,password))
    users=cursor.fetchall()
    if len(users)>0:
        session['user_id']=users[0][1]
        if 'user_id' in session:
        # return render_template('home.html')
            return redirect('/your_closet')
    return redirect('/')

@app.route('/add_user', methods=['POST'])
def add_user():
    username=request.form.get('username')
    email=request.form.get('s_email')
    password=request.form.get('s_password')

    cursor.execute("""INSERT INTO `users`(`username`, `email`, `password`) VALUES ('{}', '{}', '{}')""".format(username,email,password))
    conn.commit()

    cursor.execute(""" SELECT * from `users` where `email` LIKE '{}'""".format(email))
    myuser=cursor.fetchall()
    session['user_id']=myuser[0][1]
    os.makedirs('wardrobe_users/{}'.format(email))
    os.makedirs('wardrobe_users/{}/T-shirts'.format(email))
    os.makedirs('wardrobe_users/{}/Shirts'.format(email))
    os.makedirs('wardrobe_users/{}/Shorts'.format(email))
    os.makedirs('wardrobe_users/{}/Pants'.format(email))
    os.makedirs('wardrobe_users/{}/Jackets'.format(email))
    return redirect('/your_closet')

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')

if __name__ == "__main__":
    # init()
    app.run(debug=True)