import datetime
from email import generator
import json
import os
from pipes import quote
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
import cv2
import numpy as np
from playsound import playsound
import eel
import pyaudio
import pyautogui
import pyttsx3
import requests
import wikipedia
from engine.command import speak, takecommand
from engine.config import ASSISTANT_NAME
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat
from hugchat.login import Login
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import ctypes
import os
from datetime import datetime, timedelta
import math
import threading 
import speech_recognition as sr
import torch
import pyaudio
import struct
import pyautogui as autogui
import time


con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

       

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)




def hotword():
    porcupine = None
    paud = None
    audio_stream = None
    try:
        porcupine = pvporcupine.create(keywords=["jarvis", "alexa"])
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Listening for hotwords...")

        while True:
            audio_frame = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            audio_data = struct.unpack_from("h" * porcupine.frame_length, audio_frame)
            keyword_index = porcupine.process(audio_data)

            if keyword_index >= 0:
                print("Hotword detected!")
                autogui.keyDown("win")
                autogui.press("j")
                autogui.keyUp("win")
                time.sleep(0.5)
                
    except Exception as e:
        print("An error occurred:", e)
    
    finally:
        # Ensure cleanup even if an exception occurs
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.stop_stream()
            audio_stream.close()
        if paud is not None:
            paud.terminate()


# find contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)




import requests

def chatBot(query):
    try:
        # Convert input to lowercase for case insensitivity
        user_input = query.lower()

        # DeepSeek API configuration
        API_KEY = "sk-8858e055a5724f6ea5f526111ed1c14f"  # Replace with your actual key
        API_URL = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": user_input}],
            "temperature": 0.7
        }

        # Send request to DeepSeek API
        response = requests.post(API_URL, json=data, headers=headers)

        # Check response status
        if response.status_code == 200:
            bot_reply = response.json()["choices"][0]["message"]["content"]
        else:
            bot_reply = f"API Error: {response.status_code} - {response.text}"

        # Print and speak response
        print("Chatbot Response:", bot_reply)
        # speak(bot_reply)  # Uncomment if you have a speak() function

        return bot_reply

    except Exception as e:
        print("Error:", e)
        return "There was an issue with the chatbot."






# android automation

def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)


# to send message
def sendMessage(message, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    # open sms app
    tapEvents(136, 2220)
    #start chat
    tapEvents(819, 2192)
    # search mobile no
    adbInput(mobileNo)
    #tap on name
    tapEvents(601, 574)
    # tap on input
    tapEvents(390, 2270)
    #message
    adbInput(message)
    #send
    tapEvents(957, 1397)
    speak("message send successfully to "+name)

# news
news_api=("d7aa1073c77e4defbc62c210f8b15ae6")
def get_news():
    news_headline = []
    result = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api}").json()
    articles = result["articles"]
    for article in articles:
        news_headline.append(article["title"])
    return news_headline[:6]
#
def weather_forecast(city): 
    res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=e122282dabfd9092ab2563feba3bae3e").json()
    if 'weather' in res and len(res['weather']) > 0:
        weather = res["weather"][0]["main"]
        temp_kelvin = res["main"]["temp"]
        feels_like_kelvin = res["main"]["feels_like"]
            
        # Convert temperatures from Kelvin to Celsius
        temp = temp_kelvin - 273.15
        feels_like = feels_like_kelvin - 273.15
            
        return weather, f"{temp:.2f}°C", f"{feels_like:.2f}°C"
    else:
        raise KeyError("Weather information not found in API response")
    
def get_time():
    now = datetime.now()
    return now.strftime("%I:%M %p")  # 12-hour format with AM/PM

# Date feature
def get_date():
    today = datetime.today()
    current_date = today.strftime("%B %d, %Y")
    return f"Today's date is {current_date}"

# Google search feature
def search_google():
    speak("What do you want to search for on Google?")
    search_query = takecommand()  # Get the user's input
    url = f"https://www.google.com/search?q={search_query}"
    speak(f"Here is what I found for {search_query} on Google.")
    webbrowser.open(url)


# Wikipedia search feature
def search_wikipedia(query):
    search_term = query.replace("search for", "").strip()
    try:
        result = wikipedia.summary(search_term, sentences=2)
        speak(f"According to Wikipedia, {result}")
        return result
    except wikipedia.exceptions.DisambiguationError as e:
        speak(f"Your search term is ambiguous, try being more specific. Here are some options: {e.options[:5]}")
    except wikipedia.exceptions.PageError:
        speak(f"I couldn't find any information for {search_term} on Wikipedia.")

def mute_system():
    # Get the default audio device
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    
    # Mute the system
    volume.SetMute(1, None)
    print("System muted.")

def unmute_system():
    # Get the default audio device
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    
    # Unmute the system
    volume.SetMute(0, None)
    print("System unmuted.")

def set_volume(level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)

    # Ensure the level is within the range of 0.0 to 1.0
    volume.SetMasterVolumeLevelScalar(level / 100.0, None)
    speak(f"Volume set to {level} percent.")


def remind_user(reminder_text, reminder_time):
    """Set a reminder for a specific time."""
    current_time = datetime.now()
    wait_time = (reminder_time - current_time).total_seconds()
    
    if wait_time < 0:
        return "The reminder time has already passed."

    threading.Timer(wait_time, speak_reminder, [reminder_text]).start()
    return f"Reminder set for {reminder_time.strftime('%I:%M %p')}."

def speak_reminder(reminder_text):
    """Speak the reminder text."""
    speak(f"Reminder: {reminder_text}")

def set_alarm(alarm_time):
    """Set an alarm for a specific time."""
    current_time = datetime.now()
    wait_time = (alarm_time - current_time).total_seconds()
    
    if wait_time < 0:
        return "The alarm time has already passed."

    threading.Timer(wait_time, ring_alarm).start()
    return f"Alarm set for {alarm_time.strftime('%I:%M %p')}."

def ring_alarm():
    """Ring the alarm."""
    speak("Alarm! Time to wake up or attend to your event.")

API_KEY = "5aba876f296220"  # Replace with your actual API key

def get_location():
    """Get the current location using an external API."""
    try:
        response = requests.get(f"https://ipinfo.io/json?token={API_KEY}")
        data = response.json()
        location = f"Latitude: {data['loc'].split(',')[0]}, Longitude: {data['loc'].split(',')[1]}"
        return location
    except Exception as e:
        return "Could not retrieve location."
    



# # Set the default folder path for saving images
# DEFAULT_IMAGE_FOLDER = "D:\\jarvis folder\\ai generated images"  # Change this to your desired path

# # Image creation feature using Hugging Face API
# def create_image(prompt, folder_path=DEFAULT_IMAGE_FOLDER):  # Use the default folder path
#     try:
#         # Load the model optimized for CPU
#         pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", torch_dtype=torch.float32)
#         pipe.to("cpu")  # Ensure it's running on CPU

#         # Generate image based on prompt
#         image = pipe(prompt).images[0]

#         # Save the image with a timestamped filename
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"generated_image_{timestamp}.png"
#         file_path = os.path.join(folder_path, filename)
#         image.save(file_path)

#         print(f"Image saved as {file_path}")
#         return f"Image created and saved as {filename}"

#     except Exception as e:
#         print(f"Error in image creation: {str(e)}")
#         return "Error occurred while creating the image."




# Default folder paths
DEFAULT_PICTURE_FOLDER = "D:\\jarvis folder\\pictures"  # Change this to your desired path
DEFAULT_SCREENSHOT_FOLDER = "D:\\jarvis folder\\screenshots"  # Change this to your desired path

# Function to take a picture
def take_picture(folder_path=DEFAULT_PICTURE_FOLDER):
    """Opens the camera, takes a picture, and saves it to the specified folder."""
    try:
        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)

        # Open camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Unable to access the camera."

        speak("Opening the camera. Get ready!")
        
        # Read frame from the camera
        ret, frame = cap.read()
        if not ret:
            return "Failed to capture an image."
        
        # Save the image with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"captured_image_{timestamp}.png"
        file_path = os.path.join(folder_path, filename)
        cv2.imwrite(file_path, frame)
        
        speak(f"Picture taken and saved sucessfully")
        cap.release()
        cv2.destroyAllWindows()
        return f"Picture saved at {file_path}"
    except Exception as e:
        return f"Error taking picture: {str(e)}"

# Function to take a screenshot
def take_screenshot(folder_path=DEFAULT_SCREENSHOT_FOLDER):
    """Takes a screenshot and saves it to the specified folder."""
    try:
        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)

        speak("Taking a screenshot.")
        
        # Capture the screenshot
        screenshot = pyautogui.screenshot()
        
        # Save the screenshot with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        file_path = os.path.join(folder_path, filename)
        screenshot.save(file_path)
        
        speak(f"Screenshot taken and saved sucessfully")
        return f"Screenshot saved at {file_path}"
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"