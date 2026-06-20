import speech_recognition as sr
import pyttsx3
import os
import subprocess
import webbrowser
import pywhatkit
import sounddevice as sd
from scipy.io import wavfile
import time
import threading
import datetime
from pathlib import Path

print("[VERIFICATION] Modern Python 3.14 libraries loaded successfully.")

def speak(text):
    print(f"Jarvis: {text}")
    try:
        engine = pyttsx3.init('sapi5')
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[ERROR] Text-to-speech failed: {e}")
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as fallback_error:
            print(f"[ERROR] Fallback engine also failed: {fallback_error}")

def listen_command():
    fs = 44100  
    seconds = 4  
    temp_filename = "temp_voice.wav"

    print("\n[STATUS] Jarvis is listening (4-second window)...")
    
    try:
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  
        wavfile.write(temp_filename, fs, myrecording)

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_filename) as source:
            audio = recognizer.record(source)
        
        print("[STATUS] Processing audio...")
        command = recognizer.recognize_google(audio)
        print(f"[USER]: {command}")
        
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        return command.lower().strip()
        
    except sr.UnknownValueError:
        print("[OUTPUT] Audio heard, but intent unclear.")
        return ""
    except Exception as e:
        print(f"[STATUS] Listening window closed or reset: {e}")
        if os.path.exists(temp_filename):
            try: os.remove(temp_filename)
            except: pass
        return ""

if __name__ == "__main__":
    speak("Phase one system active. Hello Rakesh.")
    
    while True:
        command = listen_command()
        
        if not command:
            continue
            
        if any(word in command for word in ["exit", "goodbye", "stop", "power down"]):
            speak("Powering down system. Goodbye, Rakesh.")
            break
            
        elif "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The current time is {current_time}.")
            
        elif "date" in command or "today" in command:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            speak(f"Today is {current_date}.")
            
        elif "open notepad" in command:
            speak("Opening Notepad application.")
            subprocess.Popen(["notepad.exe"])
            
        elif "open chrome" in command or "open google" in command:
            speak("Launching Google Chrome browser.")
            def launch_browser():
                webbrowser.open("https://www.google.com")
            
            threading.Thread(target=launch_browser).start()
               
        elif "play" in command and ("youtube" in command or "song" in command):
            query = command.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
            if query:
                speak(f"Playing {query} on YouTube.")
                threading.Thread(target=lambda: pywhatkit.playonyt(query)).start()
            else:
                speak("What would you like me to play?")
            
        elif "your name" in command:
            speak("My name is Jarvis, your system assistant.")

        elif "my name" in command:
            speak("Your name is Rakesh.")

        elif any(greet in command for greet in ["hey jarvis", "hello jarvis", "wake up"]):
            speak("Hello Rakesh! System is fully operational. How can I assist you?")
            
        else:
            print(f"[OUTPUT] Command recognized but unmapped: '{command}'")