from flask import Flask, render_template , request , jsonify, send_file, make_response
from PIL import Image
import csv
import os , io , sys
import numpy as np 
import cv2
import base64
import json
from yolo_detection_images import runModel
from datetime import datetime
from pymongo import MongoClient
last_detection_results = None
app = Flask(__name__)
# MongoDB and GridFS setup
client = MongoClient('mongodb://localhost:27017/')
db = client['Container']
collection = db['log']


############################################## THE REAL DEAL ###############################################
@app.route('/detectObject' , methods=['POST'])
def mask_image():
    global last_detection_results
    
    img_files = request.files.getlist('image')
    results = []
    ID_nums = []
    
    for index, img_file in enumerate(img_files):
        img = load_image_from_request(img_file)
        ##################################### THAY ĐOAN NAY BANG MODEL DETECT ID
        if index == 0:
            #img_id=containernumber_detection(img, sess_d, input_x, segm_logits, link_logits, config,sess_r_h,sess_r_v,images_ph_h, images_ph_v, model_out_h, model_out_v, decoded_h, decoded_v)
            #img= detection_damage(img)
    
            id = run_ID_detection(img)
            doc_path = 'D:\Learning\container\detect_result.txt'
            with open(doc_path, 'r', encoding='utf-8') as file:
                content = file.read()
            last_ID_result = get_ID_result(content)
            ID_nums.append(last_ID_result)
            
            for ID_num in ID_nums:
                ID_data = {
                    'ID': ID_num['ID'],
                    'time': ID_num['time']
                }
            save_to_csv(ID_data)
        unique_id = ID_nums[0]['ID'] if ID_nums else 'default_id'
        unique_time = ID_nums[0]['time'] if ID_nums else datetime.now().isoformat()
        #####################################
        img = run_object_detection(img)
         # Convert both original and processed images to base64

        # Get current time
        current_time = datetime.now().isoformat()
        img_base64 = save_image_to_base64(img)

        doc_path = 'D:\Learning\container\detect_result.txt'
        with open(doc_path, 'r', encoding='utf-8') as file:
            content = file.read()

        last_detection_result = get_last_detection_result(content, img_base64)
        results.append(last_detection_result)
    
        # MongoDB document
        for result in results:
            document = {
                "ID": result['ID'],  # Replace with actual ID
                "Time": result['time'],
                "PostProcessedImage": result['status']
            }

            # Insert into MongoDB
            collection.insert_one(document)


    
    response = {
        'ID': unique_id,
        'time': unique_time,
        'images': [{'status': str(result['status'])} for result in results]
    }

    return jsonify(response)

def load_image_from_request(file):
    npimg = np.fromstring(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    return img

def run_object_detection(img):
    # Run your object detection model
    img = runModel(img)
    return img

def run_ID_detection(img):
    return img
def save_image_to_base64(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img.astype("uint8"))
    rawBytes = io.BytesIO()
    img.save(rawBytes, "JPEG")
    rawBytes.seek(0)
    img_base64 = base64.b64encode(rawBytes.read())
    return img_base64

def get_last_detection_result(content, img_base64):
    parts = content.split()
    return {
        'status': str(img_base64),
        'ID': parts[1],  # You can replace this with the actual ID
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def get_ID_result(content):
    parts = content.split()
    return {
        'ID': parts[1],  # You can replace this with the actual ID
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# The rest of your code remains unchanged

def save_to_csv(data):
    csv_path = 'D:\Learning\container\history.csv'
    fieldnames = ['ID', 'time']
    mode = 'a' if os.path.exists(csv_path) else 'w'

    with open(csv_path, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if mode == 'w':
            writer.writeheader()
        print("data:", data)
        for key, value in data.items():
            print(f"{key}: {value}")
        writer.writerow({'ID': data['ID'], 'time': data['time']})

##################################################### THE REAL DEAL HAPPENS ABOVE ######################################



@app.route('/history')
def history():
    csv_path = 'D:\Learning\container\history.csv'
    data = read_csv(csv_path)
    return render_template('history.html', data=data)
    
def read_csv(csv_path):
    data = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    return data

@app.route('/')
def home():
	return render_template('./index.html')

	
@app.after_request
def after_request(response):
    print("log: setting cors" , file = sys.stderr)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


if __name__ == '__main__':
	app.run(debug = True)