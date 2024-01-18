import BlynkLib
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


BLYNK_AUTH = 'u3JChP47Sz-pNe_CTCOWdzXtjktr4R3i'

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH,server='139.59.8.178')

@blynk.ON("connected")
def blynk_connected(ping):
    print('Blynk ready. Ping:', ping, 'ms')

@blynk.ON("disconnected")
def blynk_disconnected():
    print('Blynk disconnected')

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

@blynk.VIRTUAL_WRITE(5)
def my_write_handler(v1):
    v1_data = int(v1[0])
    print(v1_data)
    if v1_data == 5:
        drop()
    elif v1_data == 10:
        default()

while True:
    blynk.run()

