import RPi.GPIO as GPIO
import smtplib
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from gpiozero import Button, MotionSensor
from picamera import PiCamera
from time import sleep
from signal import pause

# GPIO settings
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)                     # Use BCM pin numbering
GPIO.setup(17,GPIO.IN)                     # Pin 17 - input - light sensor
GPIO.setup(20, GPIO.OUT, initial=GPIO.LOW) # Pin 20 - output - alarm
GPIO.setup(21, GPIO.OUT, initial=GPIO.LOW) # Pin 14 - output - flash LED
pir = MotionSensor(4)                      # Pin 4 - input - PIR sensor
button = Button(26)                        # Pin 26 - input - button
camera = PiCamera()

# Email variables
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USERNAME = 'mygmail@gmail.com'
GMAIL_PASSWORD = 'mypassword'

# define email sending
class Emailer:
    def sendmail(self, recipient, subject, content, image):
          
        # Create headers
        emailData = MIMEMultipart()
        emailData['Subject'] = subject
        emailData['To'] = recipient
        emailData['From'] = GMAIL_USERNAME
 
        # Attach text content
        emailData.attach(MIMEText(content))
 
        # Create image data from the defined image
        imageData = MIMEImage(open(image, 'rb').read(), 'jpg') 
        imageData.add_header('Content-Disposition', 'attachment; filename="image.jpg"')
        emailData.attach(imageData)
  
        # Connect to gmail server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()
  
        # Login to gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
  
        # Send email & exit
        session.sendmail(GMAIL_USERNAME, recipient, emailData.as_string())
        session.quit
  
sender = Emailer()

# Start the camera
camera.rotation = 180                      # Rotate photos
camera.start_preview()
i = 0                                      # Initial image couinting

# Stop the camera when pressing the button
def stop_camera():
    camera.stop_preview()
    GPIO.output(20, GPIO.LOW)
    exit()
    
def take_photo():
    GPIO.output(20, GPIO.HIGH)
    global i
    # If the environment is dark, then turn on the flash LED before taking photos
    if GPIO.input(17)==1:
        GPIO.output(21, GPIO.HIGH)
    else:
        GPIO.output(21, GPIO.LOW)
    # Take 5 photos once then save them to specified address
    for j in range(0, 5):
        i = i + 1
        camera.capture('/home/pi/Desktop/secur/image_%s.jpg' % i)      
    GPIO.output(21, GPIO.LOW)
    print('photos taken')
    # Notification when system is activated
    # Send the first photo with the email
    k = i - 4
    image = '/home/pi/Desktop/secur/image_%s.jpg' % k
    sendTo = 'hlu18@stevens.edu'
    emailSubject = "Security system triggered!"
    emailContent = "Intruder found: " + time.ctime()            # Tell the triggered time
    sender.sendmail(sendTo, emailSubject, emailContent, image)
    print("Email Sent")
    # Set sleep time
    sleep(30)
# Call stop_camera when the button is pressed
button.when_pressed = stop_camera
# Call take_photo when motion is detected
pir.when_motion = take_photo

pause()
