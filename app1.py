from flask import Flask, render_template , request , jsonify
from PIL import Image
import os , io , sys
import numpy as np 
import cv2
import base64
from yolo_detection_images import runModel
import sys
import time
import json
# import tensorflow as tf
# from detect import *
# from detect.text_recognition.model import TextRecognition
# from detect.containernumber_test_ckpt import containernumber_detection
from datetime import datetime
from pymongo import MongoClient
import csv
from predict import *
from ultralytics import YOLO
last_detection_result = None
app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['Container']
collection = db['log']

###########################################MODEL_NAME #########################################
# model_damage = YOLO('best.pt')  # pretrained YOLOv8n model
# detection_model_path = r"D:\UIT\Year4\Do_an_nhung\ContainerNumber-OCR-master\ContainernumberModels\pb_models\detection.pb"
# recognition_model_h_path = r"D:\UIT\Year4\Do_an_nhung\ContainerNumber-OCR-master\ContainernumberModels\ckpt\recognition_h\model_all.ckpt-8000"
# recognition_model_v_path = r"D:\UIT\Year4\Do_an_nhung\ContainerNumber-OCR-master\ContainernumberModels\ckpt\recognition_v\model_all.ckpt-146000"
# with tf.Graph().as_default():
# 	detection_graph_def = tf.GraphDef()
# 	with open(detection_model_path, "rb") as f:
# 		detection_graph_def.ParseFromString(f.read())
# 		tf.import_graph_def(detection_graph_def, name="")

# 	sess_d=tf.Session()
# 	init = tf.global_variables_initializer()
# 	sess_d.run(init)
# 	input_x = sess_d.graph.get_tensor_by_name("Placeholder:0")
# 	segm_logits = sess_d.graph.get_tensor_by_name("model/segm_logits/add:0")
# 	link_logits = sess_d.graph.get_tensor_by_name("model/link_logits/Reshape:0")
# bs = 4
# model = TextRecognition(is_training=False, num_classes=37)

# images_ph_h = tf.placeholder(tf.float32, [bs, 32, 240, 1])
# model_out_h = model(inputdata=images_ph_h)
# # print(model_out_h)
# saver_h = tf.train.Saver()
# sess_r_h=tf.Session()
# saver_h.restore(sess=sess_r_h, save_path=recognition_model_h_path)
# decoded_h, _ = tf.nn.ctc_beam_search_decoder(model_out_h, 60 * np.ones(bs), merge_repeated=False)
# with tf.variable_scope(tf.get_variable_scope(), reuse=True):
# 	images_ph_v = tf.placeholder(tf.float32, [bs, 32, 320, 1])
# 	model_out_v = model(inputdata=images_ph_v)
# 	saver_v = tf.train.Saver()
# 	sess_r_v=tf.Session()
# 	saver_v.restore(sess=sess_r_v, save_path=recognition_model_v_path)
# 	decoded_v, _ = tf.nn.ctc_beam_search_decoder(model_out_v, 80 * np.ones(bs), merge_repeated=False)


# # impaths = glob('samples/*.jpg')
# res_dir = "output"
# if not os.path.exists(res_dir):
# 	os.makedirs(res_dir)
# config = {}
# config['segm_conf_thr'] = 0.8
# config['link_conf_thr'] = 0.8
# config['min_area'] = 300
# config['min_height'] = 10
############################################## THE REAL DEAL ###############################################
image_processing_status = False
processed_images_base64 = []
@app.route('/detectObject' , methods=['POST'])
def handle_image_upload():
    global image_processing_status
    global last_detection_results
    img_files = request.files.getlist('image')
    results = []
    ID_nums = []
    processed_images_base64 = []
    for index, img_file in enumerate(img_files):
        img = load_image_from_request(img_file)
        image = img.copy()
        if index == 0:
            #img_id=containernumber_detection(img, sess_d, input_x, segm_logits, link_logits, config,sess_r_h,sess_r_v,images_ph_h, images_ph_v, model_out_h, model_out_v, decoded_h, decoded_v)
    
            doc_path = 'detect_result.txt'
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
        info = {
            "ID": unique_id,
            "time": unique_time
        }
        with open('id_time_info.json', 'w') as json_file:
            json.dump(info, json_file)
        img = run_object_detection(image)

        img_base64 = save_image_to_base64(img)

        doc_path = 'detect_result.txt'
        with open(doc_path, 'r', encoding='utf-8') as file:
            content = file.read()

        last_detection_result = get_last_detection_result(content, img_base64)
        processed_images_base64.append(img_base64)
        with open('processed_images.json', 'w') as file:
            json.dump(processed_images_base64, file)
        results.append(last_detection_result)
    
    for result in results:
        document = {
            "ID": result['ID'], 
            "Time": result['time'],
            "PostProcessedImage": result['status']
        }

        collection.insert_one(document)


    
    response = {
        'ID': unique_id,
        'time': unique_time,
        'images': [{'status': str(result['status'])} for result in results]
    }
    image_processing_status = True
    return jsonify(response)


def load_image_from_request(file):
    npimg = np.fromstring(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    return img

# def run_object_detection(img,model_damage):
#     img= detection_damage(img,model_damage)
#     return img
def run_object_detection(img):
    img= detection_damage(img)
    return img

def save_image_to_base64(img):
    img = np.array(img)
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img.astype("uint8"))
    rawBytes = io.BytesIO()
    img.save(rawBytes, "JPEG")
    rawBytes.seek(0)
    img_base64 = base64.b64encode(rawBytes.read()).decode('utf-8')
    return img_base64

def get_last_detection_result(content, img_base64):
    parts = content.split()
    return {
        'status': str(img_base64),
        'ID': parts[1],
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def get_ID_result(content):
    parts = content.split()
    return {
        'ID': parts[1],
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }



def save_to_csv(data):
    csv_path = r'history.csv'
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

@app.route('/getIdTimeInfo', methods=['GET'])
def get_id_time_info():
    try:
        with open('id_time_info.json', 'r') as json_file:
            info = json.load(json_file)
            return jsonify(info)
    except FileNotFoundError:
        return jsonify({"error": "Thông tin không tìm thấy"}), 404
@app.route('/getProcessedImages', methods=['GET'])
def get_processed_images():
    try:
        # Đọc danh sách base64 từ file
        with open('processed_images.json', 'r') as file:
            processed_images_base64 = json.load(file)
        return jsonify({'images': processed_images_base64})
    except IOError:
        return jsonify({'error': 'Không thể đọc file ảnh đã xử lý'}), 500

@app.route('/checkStatus', methods=['GET'])
def check_status():
    return jsonify({"status": image_processing_status})

@app.route('/test' , methods=['GET','POST'])
def test():
	print("log: got at test" , file=sys.stderr)
	return jsonify({'status':'succces'})

@app.route('/history')
def history():
    csv_path = r'history.csv'
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
	app.run(host='0.0.0.0',debug = True)