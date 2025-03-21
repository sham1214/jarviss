import pyttsx3
import speech_recognition as sr
import eel
import time
def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 174)
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()


def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening....')
        eel.DisplayMessage('listening....')
        r.pause_threshold = 2
        r.adjust_for_ambient_noise(source)
        
        audio = r.listen(source, 10, 10)

    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        eel.DisplayMessage(query)
        time.sleep(2)
       
    except Exception as e:
        return ""
    
    return query.lower()


@eel.expose
def allCommands(message=1):
    if message == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)
    else:
        query = message
        eel.senderText(query)

    try:
        # Command Handling
        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
        
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
        
        elif "news" in query:
            from engine.features import get_news
            news_headlines = get_news()
            for headline in news_headlines:
                speak(headline)
        
        elif "weather" in query:
            speak("Which city do you want to know the weather for?")
            city = takecommand()
            from engine.features import weather_forecast
            weather_info = weather_forecast(city)
            if weather_info:
                weather, temp, feels_like = weather_info
                speak(f"The weather in {city} is {weather}. The temperature is {temp} and it feels like {feels_like}.")
            else:
                speak("Sorry, I couldn't retrieve the weather information.")
        
        elif "time" in query:
            from engine.features import get_time
            current_time = get_time()
            speak(f"The current time is {current_time}.")
        
        elif "date" in query:
            from engine.features import get_date
            current_date = get_date()
            speak(current_date)
        
        elif "search google" in query or "search on google" in query or "google" in query:
            from engine.features import search_google
            search_google()
        
        elif "search for" in query or "wikipedia" in query or "tell me about" in query or "give information"in query:
            from engine.features import search_wikipedia
            search_wikipedia(query)
        
        elif "mute" in query:
            from engine.features import mute_system
            mute_system()
            speak("System muted.")
        
        elif "unmute" in query:
            from engine.features import unmute_system
            unmute_system()
            speak("System unmuted.")
        
        elif "set volume" in query or "volume" in query:
            # Extracting volume level from the query
            words = query.split()
            volume_set = False
            for word in words:
                if word.isdigit():
                    level = int(word)
                    if 0 <= level <= 100:
                        from engine.features import set_volume
                        set_volume(level)
                        speak(f"Volume set to {level} percent.")
                        volume_set = True
                        break
                    else:
                        speak("Please provide a valid volume level between 0 and 100.")
                        return

            if not volume_set:
                speak("Please provide a valid volume level.")
            

        elif "calculate" in query:
            from engine.features import calculate
            speak("What do you want to calculate?")
            expression = takecommand()  # Get the expression from the user
            result = calculate(expression)
            if isinstance(result, (int, float)):
                speak(f"The result is: {result}")
            else:
                speak(result)  # Speak the error message if there is one

        elif "convert" in query:
            from engine.features import convert_units
            speak("Please tell me the value and the units you want to convert.")
            conversion_query = takecommand()
            # Process the conversion query
            words = conversion_query.split()
            if len(words) >= 5 and words[1].replace('.', '', 1).isdigit():
                value = float(words[1])
                from_unit = words[2]
                to_unit = words[4]
                result = convert_units(value, from_unit, to_unit)
                speak(f"{value} {from_unit} is equal to {result} {to_unit}.")
            else:
                speak("I couldn't understand the conversion request.")
         
        elif "object detection" in query or "detect objects" in query:
            from engine.features import object_detection_with_camera
            speak("Starting object detection with the camera.")
            object_detection_with_camera()
        
        elif "set reminder" in query:
            from datetime import datetime
            speak("What is the reminder?")
            reminder_text = takecommand()
            speak("At what time? Please say in AM/PM format.")
            reminder_time = takecommand()

            # Preprocess reminder time to remove periods and convert to uppercase
            reminder_time = reminder_time.replace(".", "").upper()
            reminder_time = datetime.strptime(reminder_time, "%I:%M %p")

            current_time = datetime.now()
            reminder_time = reminder_time.replace(year=current_time.year, month=current_time.month, day=current_time.day)
            from engine.features import remind_user
            response = remind_user(reminder_text, reminder_time)
            speak(response)
        
        elif "schedule my day" in query:
            from engine.features import schedule_tasks
            schedule_tasks()
        
        elif "show my schedule" in query:
            from engine.features import show_schedule
            show_schedule()
        
        elif "take a picture" in query:
            from engine.features import take_picture
            response = take_picture()
            print(response)

        elif "take a screenshot" in query:
            from engine.features import take_screenshot
            response = take_screenshot()
            print(response)        
        
        elif "set alarm" in query:
            from datetime import datetime
            from engine.features import set_alarm
            speak("What time should I set the alarm for? Please say in AM/PM format.")
            alarm_time = takecommand()

            # Preprocess alarm time to remove periods and convert to uppercase
            alarm_time = alarm_time.replace(".", "").upper()
            alarm_time = datetime.strptime(alarm_time, "%I:%M %p")

            current_time = datetime.now()
            alarm_time = alarm_time.replace(year=current_time.year, month=current_time.month, day=current_time.day)

            response = set_alarm(alarm_time)
            speak(response)

        elif "track location" in query:
            from engine.features import get_location
            speak("Retrieving your location...")
            location = get_location()  # Call the function to get the location
            speak(f"Your current location is: {location}")

        elif "translate" in query:
            from engine.features import translate_text
            speak("Please say the text you want to translate.")
            text_to_translate = takecommand()
            if text_to_translate:
                speak("Which language do you want to translate to?")
                dest_language = takecommand()

                language_codes = {
                    "french": "fr",
                    "spanish": "es",
                    "german": "de",
                    "hindi": "hi",
                    "english": "en",
                    "urdu": "ur",
                }

                if dest_language in language_codes:
                    dest_lang_code = language_codes[dest_language]
                    translated_text = translate_text(text_to_translate, dest_lang=dest_lang_code)
                    if translated_text:
                        speak(f"The translation is: {translated_text}")
                    else:
                        speak("I couldn't retrieve the translation.")
                else:
                    speak("Sorry, I do not support that language.")
            else:
                speak("I didn't catch the text to translate.")

        elif "create image" in query:
            speak("Please describe the image you want to create.")
            image_description = takecommand()  # Get image description
            if image_description:
                from engine.features import create_image
                speak("Creating the image based on your description...")
                create_image(image_description)
                speak("The image has been created.")

        else:
            from engine.features import chatBot
            chatBot(query)

    except Exception as e:
        speak("Sorry, an error occurred while processing your request.")
        print(f"Error: {e}")

    eel.ShowHood()