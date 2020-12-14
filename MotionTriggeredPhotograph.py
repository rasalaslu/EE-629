import RPi.GPIO as GPIO
from gpiozero import Button, MotionSensor
from picamera import PiCamera
from time import sleep
from signal import pause

GPIO.setwarnings(False)                    # Ignore warning for LED pin setting
GPIO.setmode(GPIO.BCM)                     # Use BCM pin numbering
GPIO.setup(17,GPIO.IN)                     # Set pin 17 as the input pin of photoresistor
GPIO.setup(14, GPIO.OUT, initial=GPIO.LOW) # Set pin 14 as the output pin for LED and set initial value to low (off)
button = Button(2)                         # Set pin 2 as the input pin of button
pir = MotionSensor(4)                      # Set pin 4 as the input pin of PIR sensor
camera = PiCamera()

# Start the camera
camera.rotation = 0                        # Rotate the taken photo
camera.start_preview()
i = 0                                      # Initial counting image names

# Stop the camera when the button is pressed
def stop_camera():
    camera.stop_preview()
    exit()
    
def take_photo():
    global i
    # If the environment is dark, then turn on the LED before taking photos
    if GPIO.input(17)==1:
        GPIO.output(14, GPIO.HIGH)
    else:
        GPIO.output(14, GPIO.LOW)
    # Take five photos at a time and save them to specified address
    for j in range(0, 5):
        i = i + 1
        camera.capture('/home/pi/Pictures/image_%s.jpg' % i)      
    GPIO.output(14, GPIO.LOW)
    print('A photo has been taken')
    sleep(5)                               # Set the pause time as same as the minimal delay time of the sensor, 5s

button.when_pressed = stop_camera          # Run function stop_camera when the button is pressed
pir.when_motion = take_photo               # Run function take_photo when motion is detected

pause()