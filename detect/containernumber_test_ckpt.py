import cv2
import time
import tensorflow as tf
from glob import glob
from detect.detection_test_pb import detection
from detect.recognition_test_pb import recognition

import os
import numpy as np
from tqdm import tqdm
# import os, sys
# BASE_DIR = os.path.dirname(osD:\UIT\Year4\Do_an_nhung\code_man\webapp\detect\containernumber_test_ckpt.pycd.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)
res_txt = open('detect_result.txt', 'w')
def containernumber_detection(im, sess_d, input_x, segm_logits, link_logits, config,sess_r_h,sess_r_v,images_ph_h, images_ph_v, model_out_h, model_out_v, decoded_h, decoded_v):


    total_time1 = time.time() 

    # imname = os.path.basename(impath)
    # im = cv2.imread(impath)
    t1 = time.time()
    bboxs = detection(im, sess_d, input_x, segm_logits, link_logits, config)
    for bbox in bboxs:
        pts = [int(p) for p in bbox.split(",")]
        cv2.rectangle(im, (pts[0], pts[1]), (pts[4], pts[5]), (0, 255, 0), 2)
    
    t2 = time.time()
    print('detection_time: ', (t2-t1),'result', bboxs)
    
    predicted = recognition(im, sess_r_h, sess_r_v , bboxs, (240, 32), images_ph_h, images_ph_v, model_out_h, model_out_v, decoded_h, decoded_v)
    cv2.putText(im, predicted, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    t3 = time.time()
    print('recognition_time: ', (t3-t2),'result', predicted)
    line = 'a.jpg' + ' ' + predicted + '\n'
    with open('detect_result.txt', 'w') as res_txt:
        res_txt.write(line)
    return im
        # cv2.imwrite(os.path.join("output", imname), im)
        
    
    total_time2 = time.time()
    print('total_time: ', (total_time2 - total_time1))
    
if __name__ == "__main__":
    import sys
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_DIR)

# from accuracy import acc
# acc('containernumber_result.txt')
