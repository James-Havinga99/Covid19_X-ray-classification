from flask import Flask, render_template, request,jsonify
from tensorflow.keras.models import load_model
import cv2
import numpy as np
import base64
from PIL import Image
import io
import re
import os

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
img_size=100

app = Flask(__name__) 

def get_model():
	global model
	model=load_model('model\model-015.model')
	print("Model Loaded")

label_dict={0:'Covid-19 Negative', 1:'Covid-19 Positive'}

def preprocess(img):

	img=np.array(img)


	if(img.ndim==3):
		gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	else:
		gray=img

	gray=gray/255
	print(gray.shape)
	resized=cv2.resize(gray,(img_size,img_size))
	reshaped=resized.reshape(1,img_size,img_size)
	return reshaped

print("Loading Keras model...")
get_model()

@app.route("/")
def index():
	return(render_template("index.html"))

@app.route("/predict", methods=["POST"])
def predict():
	message = request.get_json(force=True)
	encoded = message['image']
	decoded = base64.b64decode(encoded)
	dataBytesIO=io.BytesIO(decoded)
	dataBytesIO.seek(0)
	image = Image.open(dataBytesIO)

	test_image=preprocess(image)

	prediction = model.predict(test_image)
	result=np.argmax(prediction,axis=1)[0]
	accuracy=float(np.max(prediction,axis=1)[0])

	label=label_dict[result]

	print(prediction,result,accuracy)

	response = {'prediction': {'result': label,'accuracy': accuracy}}

	return jsonify(response)

app.run(debug=True)

# To Run:
# conda activate tensorflow
# pyhton app.py