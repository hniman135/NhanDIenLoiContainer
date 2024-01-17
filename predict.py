
from ultralytics import YOLO
from PIL import Image
# Load a model
model = YOLO('best.pt')  # pretrained YOLOv8n model
def detection_damage(image):
# Run batched inference on a list of images
    results = model([image])  # return a list of Results objects

    # Process results list
    for result in results:
        boxes = result.boxes  # Boxes object for bbox outputs
        masks = result.masks  # Masks object for segmentation masks outputs
        keypoints = result.keypoints  # Keypoints object for pose outputs
        probs = result.probs  # Probs object for classification outputs
    # Show the results
    for r in results:
        im_array = r.plot()  # plot a BGR numpy array of predictions
    im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
    return im
#detection_damage(r'D:\UIT\Year4\Do_an_nhung\code\file_run\runs\detect\train5\weights\1.jpg')