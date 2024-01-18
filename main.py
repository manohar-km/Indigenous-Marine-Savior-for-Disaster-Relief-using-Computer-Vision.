import numpy as np
import imutils
import time
import cv2
from imutils.video import VideoStream
from threading import Thread
from espeak import espeak
import requests
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


# setup PWM process
base = 26
servo_1 = 19
servo_2 = 13
grip = 6
GPIO.setup(base,GPIO.OUT)
pwm1 = GPIO.PWM(base,50) # 50 Hz (20 ms PWM period)
GPIO.setup(servo_1,GPIO.OUT)
pwm2 = GPIO.PWM(servo_1,50) # 50 Hz (20 ms PWM period)
GPIO.setup(servo_2,GPIO.OUT)
pwm3 = GPIO.PWM(servo_2,50) # 50 Hz (20 ms PWM period)
GPIO.setup(grip,GPIO.OUT)
pwm4 = GPIO.PWM(grip,50) # 50 Hz (20 ms PWM period)
pwm1.start(3)
pwm2.start(8)
pwm3.start(3)
pwm4.start(12)

def drop():
    pwm4.ChangeDutyCycle(9)
    pwm1.ChangeDutyCycle(12)
    pwm2.ChangeDutyCycle(3)
    pwm3.ChangeDutyCycle(5)
    time.sleep(1)
    pwm4.ChangeDutyCycle(12)

def default():
    pwm1.ChangeDutyCycle(3)
    pwm2.ChangeDutyCycle(8)
    pwm3.ChangeDutyCycle(3)
    pwm4.ChangeDutyCycle(12)
    time.sleep(1)
    pwm4.ChangeDutyCycle(9)
	
# load the COCO class labels our YOLO model was trained on
LABELS = open("coco.names").read().strip().split("\n")

# load our YOLO object detector trained on COCO dataset (80 classes)
print("[INFO] loading YOLO from disk...")
net = cv2.dnn.readNetFromDarknet("person.cfg", "person.weights")

# initialize a list of colors to represent each possible class label
np.random.seed(42)
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
	dtype="uint8")

ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# initialize the video stream, pointer to output video file, and
# frame dimensions
vs = VideoStream(src=0).start()
#vs = cv2.VideoCapture(0)
(W, H) = (None, None)

def push_online(object_detected):
	try:
		print("updated",object_detected)
		val = requests.get("https://blynkserver.website:9443/u3JChP47Sz-pNe_CTCOWdzXtjktr4R3i/get/V1",verify=False)
		lat = val.content[2:12]
		lon = val.content[13:23]
		print(lat)
		print(lon)
		val = requests.get("https://blynkserver.website:9443/u3JChP47Sz-pNe_CTCOWdzXtjktr4R3i/update/V2?value=1&value="+str(lat.decode('utf-8'))+"&value="+str(lon.decode('utf-8'))+"&value="+object_detected,verify=False)
	except Exception as e:
		print(e)
	
def update_location(object_detected):
	    t = Thread(target = push_online,args=[object_detected])
	    t.deamon = True
	    t.start()
cnt = 0
while True:
	# read the next frame from the file
	frame = vs.read()
	frame = imutils.resize(frame, width=400)

	# if the frame dimensions are empty, grab them
	if W is None or H is None:
		(H, W) = frame.shape[:2]
		# construct a blob from the input frame and then perform a forward
	# pass of the YOLO object detector, giving us our bounding boxes
	# and associated probabilities
	blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (224, 224),
		swapRB=True, crop=False)
	net.setInput(blob)
	start = time.time()
	layerOutputs = net.forward(ln)
	end = time.time()
 
	# initialize our lists of detected bounding boxes, confidences,
	# and class IDs, respectively
	boxes = []
	confidences = []
	classIDs = []
	centers = []
	# loop over each of the layer outputs
	for output in layerOutputs:
		# loop over each of the detections
		for detection in output:
			# extract the class ID and confidence (i.e., probability)
			# of the current object detection
			scores = detection[5:]
			classID = np.argmax(scores)
			confidence = scores[classID]
 
			# filter out weak predictions by ensuring the detected
			# probability is greater than the minimum probability
			if confidence > 0.4 and classID == 0:
				# scale the bounding box coordinates back relative to
				# the size of the image, keeping in mind that YOLO
				# actually returns the center (x, y)-coordinates of
				# the bounding box followed by the boxes' width and
				# height
				box = detection[0:4] * np.array([W, H, W, H])
				(centerX, centerY, width, height) = box.astype("int")
 
				# use the center (x, y)-coordinates to derive the top
				# and and left corner of the bounding box
				x = int(centerX - (width / 2))
				y = int(centerY - (height / 2))
 
				# update our list of bounding box coordinates,
				# confidences, and class IDs
				boxes.append([x, y, int(width), int(height)])
				confidences.append(float(confidence))
				classIDs.append(classID)
				centers.append((centerX, centerY))

				# apply non-maxima suppression to suppress weak, overlapping
	# bounding boxes
	idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)
	# ensure at least one detection exists
	if len(idxs) > 0:
		# loop over the indexes we are keeping
		for i in idxs.flatten():
			# extract the bounding box coordinates
			(x, y) = (boxes[i][0], boxes[i][1])
			(w, h) = (boxes[i][2], boxes[i][3])
			# draw a bounding box rectangle and label on the frame
			color = [int(c) for c in COLORS[classIDs[i]]]
			cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
			text = "{}: {:.4f}".format(LABELS[classIDs[i]],
				confidences[i])
			cv2.putText(frame, text, (x, y - 5),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
			update_location(LABELS[classIDs[i]])
			cnt += 1
			if cnt % 5 == 0:
				print("dropping jacket")
				drop()
				time.sleep(1)
				default()
				cnt = 0
	cv2.imshow("Image", frame)
	key = cv2.waitKey(1) & 0xFF
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
			break
# release the file pointers
print("[INFO] cleaning up...")
vs.stop()
cv2.destroyAllWindows()
