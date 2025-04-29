import datetime
import cv2
import time
from time import sleep
import os
import RPi.GPIO as GPIO
import sys
from prog_files import controls

sys.dont_write_bytecode = True


def capture_and_save(directory="images", max_images=18):
  
  if not os.path.exists(directory):
    os.makedirs(directory)

  image_files = [f for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
  
  if len(image_files) >= max_images:
    oldest_image = min(image_files, key=lambda f: os.path.getctime(os.path.join(directory, f)))
    os.remove(os.path.join(directory, oldest_image))

 # Check if LED is already on before turning it on
  currentDateAndTime = datetime.datetime.now()
  current_hour = currentDateAndTime.hour
  if 9 <= current_hour < 21:  # Check if the current hour is between 9 and 20 (inclusive)
      camera = cv2.VideoCapture(0)
      camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
      camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
      time.sleep(0.5)
      ret, frame = camera.read()
      camera.release()

  else:
      controls.led_output(True)
      lcamera = cv2.VideoCapture(0)
      camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
      camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
      time.sleep(0.5)
      ret, frame = camera.read()
      camera.release()
      controls.led_output(False)



  


  if ret:
    timestamp = time.strftime("%H:%M %d-%m-%y")
    filename = f"{timestamp}.jpg"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0
    font_color = (255, 255, 255)  # White color
    thickness = 2
    (text_width, text_height), _ = cv2.getTextSize(timestamp, font, font_scale, thickness)

    text_x = int((frame.shape[1] - text_width) / 2)
    text_y = int((frame.shape[0] + text_height) / 2)

    cv2.putText(frame, timestamp, (text_x, text_y), font, font_scale, font_color, thickness)
    filepath = os.path.join(directory, filename)

    cv2.imwrite(filepath, frame)
    #print(f"Image saved as {filepath}")
  else:
    print("Failed to capture image.")



