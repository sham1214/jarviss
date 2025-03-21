import os
import eel
import subprocess
import atexit
import signal

from engine.features import *
from engine.command import *
from engine.auth import recoganize

# Global variables to store process handles
device_process = None

def start():
    global device_process

    eel.init("www")

    playAssistantSound()

    @eel.expose
    def init():
        global device_process  
        device_process = subprocess.Popen(
            [r'device.bat'], 
            creationflags=subprocess.CREATE_NEW_CONSOLE  # Start in a new window (Windows only)
        )
        eel.hideLoader()
        speak("Ready for Face Authentication")
        flag = recoganize.AuthenticateFace()
        if flag == 1:
            eel.hideFaceAuth()
            speak("Face Authentication Successful")
            eel.hideFaceAuthSuccess()
            speak("Hello, Welcome Sham, How can I Help You")
            eel.hideStart()
            playAssistantSound()
        else:
            speak("Face Authentication Fail")

    # Open Edge
    os.system('start msedge.exe --app="http://localhost:8000/index.html"')

    # Cleanup function to ensure all processes are stopped
    def cleanup():
        print("Cleaning up processes...")

        # Kill device.bat process
        if device_process and device_process.poll() is None:
            print("Stopping device.bat process...")
            device_process.terminate()

        # Kill Edge browser
        os.system("taskkill /IM msedge.exe /F")

        # Stop Eel server
        os.kill(os.getpid(), signal.SIGTERM)

    atexit.register(cleanup)  # Ensure cleanup runs when script exits

    eel.start('index.html', mode=None, host='localhost', block=True)

# Start the application
start()
